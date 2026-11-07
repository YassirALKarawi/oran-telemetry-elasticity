"""Independent paired validation of the three frozen transport policies."""
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "reservation"))
sys.path.insert(0, str(HERE.parent / "adaptive"))
from floor_trial import trial
from policy import choose


def summarize(rows, protocol):
    output = {}
    for speed in protocol["transition_speeds"]:
        output[speed] = {}
        speed_rows = [row for row in rows if row["speed"] == speed]
        for method in protocol["policies"]:
            traces = []
            for seed in protocol["seeds_by_speed"][speed]:
                windows = [row for row in speed_rows
                           if row["method"] == method and row["seed"] == seed]
                assert len(windows) == protocol["windows_per_trace"]
                counts = []
                for class_index, deadline in enumerate(protocol["deadlines_ms"]):
                    sent = sum(row["sent"][class_index] for row in windows)
                    received = sum(row["received"][class_index] for row in windows)
                    timely = 0
                    for row in windows:
                        histogram = row["delay_ms_ceiling_histogram"][class_index]
                        assert sum(histogram.values()) == row["received"][class_index]
                        timely += sum(value for ceiling, value in histogram.items()
                                      if int(ceiling) <= deadline)
                    counts.append({"sent": sent, "timely": timely,
                                   "late": received - timely,
                                   "missing": sent - received})
                rates = [100 * count["timely"] / count["sent"] for count in counts]
                rates.append(100 * sum(count["timely"] for count in counts)
                             / sum(count["sent"] for count in counts))
                traces.append({"seed": seed, "counts": counts, "rates": rates})
            output[speed][method] = {
                "traces": traces,
                "means": [statistics.mean(trace["rates"][index] for trace in traces)
                          for index in range(3)],
                "sample_sd": [statistics.stdev(trace["rates"][index] for trace in traces)
                              for index in range(3)],
            }
    return output


def main():
    protocol_path = HERE / "independent_protocol.json"
    protocol = json.loads(protocol_path.read_text())
    assert protocol["policies"] == ["adaptive", "thesis_floor", "proportional_floor"]
    assert protocol["deadlines_ms"] == [15, 40]
    assert protocol["budget_mbps"] == 16 and protocol["floor_pct"] == 40
    assert len(protocol["traces"]) == 18
    trial.setup()
    executable = next(Path("build").rglob("xapp_mac_ctrl"))
    events = Path(os.environ["E2_SHARE_EVENTS"])
    issued = []
    rows = []
    with (trial.OUT / "independent.jsonl").open("x") as ledger:
        for trace in protocol["traces"]:
            assert sorted(trace["order"]) == sorted(protocol["policies"])
            for method in trace["order"]:
                active = 10
                trial.apply(active)
                for epoch, rates in enumerate(trace["rates_mbps"]):
                    result = trial.traffic(rates)
                    assert result["sent"] == [rate * 250 for rate in rates]
                    assert abs(result["elapsed"] - trial.DURATION) < 0.05 * trial.DURATION
                    thesis, report, _ = trial.decide(result, epoch)
                    selected = choose(method, thesis, result["sent"], result["received"])
                    row = dict(speed=trace["speed"], method=method, seed=trace["seed"],
                               epoch=epoch, active=active, thesis=thesis, selected=selected,
                               report=report, rates=rates, **result)
                    if epoch + 1 < len(trace["rates_mbps"]):
                        log = trial.OUT / f'control-{trace["seed"]}-{method}-{epoch}.log'
                        with log.open("w") as stream:
                            subprocess.run([executable], env={**os.environ,
                                           "E2_SHARE": str(selected)}, stdout=stream,
                                           stderr=subprocess.STDOUT, timeout=15, check=True)
                        assert "CONTROL ACK rx" in log.read_text()
                        issued.append(selected)
                        decoded = list(map(int, events.read_text().splitlines()))
                        assert decoded == issued
                        row["applied_next"] = trial.apply(decoded[-1])
                        active = decoded[-1]
                    rows.append(row)
                    print(json.dumps(row), file=ledger, flush=True)
    assert len(rows) == 432 and len(issued) == 378
    (trial.OUT / "independent-scores.json").write_text(
        json.dumps(summarize(rows, protocol), indent=2))
    host = {
        "runner_os": os.environ.get("RUNNER_OS"),
        "runner_arch": os.environ.get("RUNNER_ARCH"),
        "image_os": os.environ.get("ImageOS"),
        "image_version": os.environ.get("ImageVersion"),
        "python": platform.python_version(),
        "kernel": platform.release(),
        "protocol_sha256": hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
    }
    (trial.OUT / "host.json").write_text(json.dumps(host, indent=2))


if __name__ == "__main__":
    main()
