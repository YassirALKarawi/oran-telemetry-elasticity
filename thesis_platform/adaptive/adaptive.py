"""Three-arm paired replay on frozen transport loads."""
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "reservation"))
from floor_trial import metrics, trial
from policy import choose


def main():
    protocol = json.loads((HERE/"protocol.json").read_text())
    trial.setup()
    exe = next(Path("build").rglob("xapp_mac_ctrl"))
    events = Path(os.environ["E2_SHARE_EVENTS"])
    issued = []
    rows = []
    with (trial.OUT/"factorial.jsonl").open("x") as ledger:
        for trace in protocol["traces"]:
            for method in trace["order"]:
                active = 10
                trial.apply(active)
                for epoch,rates in enumerate(trace["rates_mbps"]):
                    r = trial.traffic(rates)
                    assert r["sent"] == [v*250 for v in rates]
                    assert abs(r["elapsed"]-trial.DURATION) < 0.05*trial.DURATION
                    thesis,report,_ = trial.decide(r,epoch)
                    selected = choose(method, thesis, r["sent"], r["received"])
                    row = dict(method=method,seed=trace["seed"],epoch=epoch,active=active,
                               thesis=thesis,selected=selected,report=report,rates=rates,**r)
                    if epoch+1 < len(trace["rates_mbps"]):
                        log = trial.OUT/f'control-{trace["seed"]}-{method}-{epoch}.log'
                        with log.open("w") as stream:
                            subprocess.run([exe],env={**os.environ,"E2_SHARE":str(selected)},
                                           stdout=stream,stderr=subprocess.STDOUT,timeout=15,check=True)
                        assert "CONTROL ACK rx" in log.read_text()
                        issued.append(selected)
                        decoded=list(map(int,events.read_text().splitlines()))
                        assert decoded==issued
                        row["applied_next"]=trial.apply(decoded[-1])
                        active=decoded[-1]
                    rows.append(row)
                    print(json.dumps(row),file=ledger,flush=True)
    scores=metrics(rows,protocol["deadlines_ms"])
    (trial.OUT/"factorial-scores.json").write_text(json.dumps(scores,indent=2))
    assert len(issued)==72


if __name__=="__main__":
    main()
