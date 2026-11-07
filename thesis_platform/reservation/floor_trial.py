"""Choose a reservation on development loads and evaluate the frozen variant."""
import hashlib
import json
import os
import statistics
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "transport_shares"))
import trial


def metrics(rows, limits):
    by_method = {}
    for method in sorted({r["method"] for r in rows}):
        traces = []
        for seed in sorted({r["seed"] for r in rows}):
            windows = [r for r in rows if (r["method"], r["seed"]) == (method, seed)]
            assert len(windows) == 5
            counts = []
            for i, limit in enumerate(limits):
                sent = sum(r["sent"][i] for r in windows)
                received = sum(r["received"][i] for r in windows)
                timely = 0
                for r in windows:
                    h = r["delay_ms_ceiling_histogram"][i]
                    assert sum(h.values()) == r["received"][i]
                    timely += sum(v for k,v in h.items() if int(k) <= limit)
                counts.append(dict(sent=sent, timely=timely, late=received-timely, missing=sent-received))
            rates = [100*c["timely"]/c["sent"] for c in counts]
            rates.append(100*sum(c["timely"] for c in counts)/sum(c["sent"] for c in counts))
            traces.append(dict(seed=seed, counts=counts, rates=rates))
        by_method[method] = dict(traces=traces, means=[statistics.mean(t["rates"][i] for t in traces) for i in range(3)])
    return by_method


def select(development, protocol):
    means = {k:v["means"] for k,v in development.items()}
    target = means["proportional"][0] + max(0, means["thesis"][0]-means["proportional"][0])/2
    floors = protocol["class2_floor_units"]
    eligible = [f for f in floors if means[f"floor{f}"][0] >= target]
    if eligible:
        winner = max(eligible, key=lambda f:(means[f"floor{f}"][1],-f))
    else:
        winner = max(floors,key=lambda f:(means[f"floor{f}"][0],means[f"floor{f}"][1],-f))
    return dict(units=winner, target_class1=target, eligible=eligible, development_means=means)


def run():
    protocol = json.loads((HERE/"protocol.json").read_text())
    trial.setup()
    exe = next(Path("build").rglob("xapp_mac_ctrl"))
    events = Path(os.environ["E2_SHARE_EVENTS"])
    expected_events = []
    floor = None
    for phase in ("development","evaluation"):
        rows = []
        with (trial.OUT/f"{phase}.jsonl").open("x") as ledger:
            for trace in protocol["phases"][phase]:
                for method in trace["order"]:
                    active = 10
                    trial.apply(active)
                    for epoch, rates in enumerate(trace["rates_mbps"]):
                        result = trial.traffic(rates)
                        assert result["sent"] == [r*250 for r in rates]
                        assert abs(result["elapsed"]-trial.DURATION) < .05*trial.DURATION
                        thesis, report, _ = trial.decide(result,epoch)
                        a,b = result["sent"]
                        proportional = max(1,min(19,(40*a+a+b)//(2*(a+b))))
                        action = thesis
                        if method == "proportional":
                            action = proportional
                        elif method == "guarded" or method.startswith("floor"):
                            reserve = floor if method=="guarded" else int(method[5:])
                            action = min(thesis,20-reserve)
                        row = dict(seed=trace["seed"], method=method, epoch=epoch, rates=rates,
                                   active=active, thesis=thesis, proportional=proportional, report=report, **result)
                        if epoch < len(trace["rates_mbps"])-1:
                            log = trial.OUT/f'control-{trace["seed"]}-{method}-{epoch}.log'
                            with log.open("w") as stream:
                                subprocess.run([exe],env={**os.environ,"E2_SHARE":str(action)},stdout=stream,
                                               stderr=subprocess.STDOUT,timeout=15,check=True)
                            assert "CONTROL ACK rx" in log.read_text()
                            expected_events.append(action)
                            decoded=list(map(int,events.read_text().splitlines()))
                            assert decoded==expected_events
                            row["applied_next"]=trial.apply(decoded[-1])
                            active=decoded[-1]
                        rows.append(row)
                        print(json.dumps(row),file=ledger,flush=True)
        scores=metrics(rows,protocol["class_deadlines_ms"])
        (trial.OUT/f"{phase}-scores.json").write_text(json.dumps(scores,indent=2))
        if phase=="development":
            selection=select(scores,protocol)
            path=trial.OUT/"selection.json"
            path.write_text(json.dumps(selection,indent=2))
            floor=json.loads(path.read_text())["units"]
            print("Frozen selection before evaluation",floor,hashlib.sha256(path.read_bytes()).hexdigest(),flush=True)
    assert len(expected_events)==132


if __name__=="__main__":
    run()
