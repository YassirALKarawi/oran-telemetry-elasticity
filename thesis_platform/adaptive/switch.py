import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

from policy import choose

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "sdn"))
import sdn


def counters(epoch, when):
    values = []
    for meter in [1, 2]:
        raw = sdn.of("meter-stats", f"meter={meter}")
        (sdn.OUT/f"{epoch}-{when}-meter-{meter}.txt").write_text(raw)
        values.append([int(re.search(key+r"[:=]\s*(\d+)",raw).group(1))
                       for key in ["packet_in_count","packet_count"]])
    return values


def main():
    protocol = json.loads((HERE/"protocol.json").read_text())
    loads = protocol["switch_loads"]
    sdn.setup()
    exe = next(Path("build").rglob("xapp_mac_ctrl"))
    issued = []
    active = 10
    with (sdn.OUT/"switch.jsonl").open("x") as ledger:
        for epoch,rates in enumerate(loads):
            before = counters(epoch,"start")
            row = sdn.trial.traffic(rates)
            after = counters(epoch,"end")
            for i in range(2):
                packets, drops = [b-a for a,b in zip(before[i],after[i])]
                assert packets == row["sent"][i] == rates[i]*250
                assert 0 <= drops <= packets-row["received"][i]
            row.update(epoch=epoch,rates=rates,active=active)
            if epoch < len(loads)-1:
                start = time.monotonic()
                thesis, report, _ = sdn.trial.decide(row,epoch)
                selected = choose("adaptive",thesis,row["sent"],row["received"])
                log = sdn.OUT/f"control-{epoch}.log"
                with log.open("w") as stream:
                    subprocess.run([exe],env={**os.environ,"E2_SHARE":str(selected)},
                                   stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=20)
                assert "CONTROL ACK rx" in log.read_text()
                issued.append(selected)
                decoded = list(map(int,Path(os.environ["E2_SHARE_EVENTS"]).read_text().splitlines()))
                assert issued == decoded
                sdn.meters(decoded[-1],"mod")
                row["command_to_readback_s"] = time.monotonic()-start
                (sdn.OUT/"meters-mod.txt").rename(sdn.OUT/f"meters-{epoch}.txt")
                active=decoded[-1]
                row.update(thesis=thesis,selected=selected,report=report)
            print(json.dumps(row),file=ledger,flush=True)


if __name__ == "__main__":
    main()
