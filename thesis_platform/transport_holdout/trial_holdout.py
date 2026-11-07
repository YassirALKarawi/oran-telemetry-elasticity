"""Run the frozen paired traces through the existing Linux and FlexRIC fixture."""
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "transport_shares"))
import trial


def run():
    protocol = json.loads((HERE / "protocol.json").read_text())
    trial.setup()
    exe = next(Path("build").rglob("xapp_mac_ctrl"))
    events = Path(os.environ["E2_SHARE_EVENTS"])
    expected_events = []
    output = trial.OUT / "holdout.jsonl"
    with output.open("x") as ledger:
        for trace in protocol["traces"]:
            for method in trace["order"]:
                active = 10
                trial.apply(active)
                for epoch, rates in enumerate(trace["rates_mbps"]):
                    result = trial.traffic(rates)
                    expected = [int(r*1e6*trial.DURATION/(8*trial.SIZE)) for r in rates]
                    assert result["sent"] == expected
                    assert abs(result["elapsed"] - trial.DURATION) < 0.05 * trial.DURATION
                    thesis, report, diagnostic = trial.decide(result, epoch)
                    total = sum(result["sent"])
                    proportional = max(1, min(19, (40 * result["sent"][0] + total) // (2 * total)))
                    row = dict(seed=trace["seed"], method=method, epoch=epoch, rates=rates,
                               active=active, report=report, thesis=thesis, proportional=proportional,
                               diagnostic=diagnostic, **result)
                    if epoch + 1 < len(trace["rates_mbps"]):
                        selected = thesis if method == "thesis" else proportional
                        log = trial.OUT / f'control-{trace["seed"]}-{method}-{epoch}.log'
                        with log.open("w") as stream:
                            subprocess.run([exe], env={**os.environ,"E2_SHARE":str(selected)},
                                           stdout=stream, stderr=subprocess.STDOUT, timeout=15, check=True)
                        assert "CONTROL ACK rx" in log.read_text()
                        expected_events.append(selected)
                        decoded = list(map(int,events.read_text().splitlines()))
                        assert decoded == expected_events
                        row["applied_next"] = trial.apply(decoded[-1])
                        active = decoded[-1]
                    print(json.dumps(row), file=ledger, flush=True)
    assert len(expected_events) == 60


if __name__ == "__main__":
    run()
