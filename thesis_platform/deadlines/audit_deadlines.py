"""Compute paired on-time delivery from integer-ms upper-bound histograms."""
import json
from pathlib import Path
from statistics import mean

PROFILES = {"model_slot_projection": (1500,4000), "tight_sensitivity": (15,40)}
METHODS = ("thesis","proportional")


def audit(folder):
    traces = json.loads((folder/"protocol.json").read_text())["traces"]
    rows = [json.loads(s) for s in (folder/"holdout.jsonl").read_text().splitlines()]
    assert len(rows) == 72
    index = {(r["seed"],r["method"],r["epoch"]):r for r in rows}
    assert len(index)==len(rows)
    events = [r["applied_next"][0] for r in rows if "applied_next" in r]
    assert len(events)==60 and events==list(map(int,(folder/"agent-actions.txt").read_text().splitlines()))
    frames = (folder/"frames.tsv").read_text().lower()
    assert frames.count("riccontrolrequest")==frames.count("riccontrolacknowledge")==60
    outputs = {}
    for name,deadlines in PROFILES.items():
        paired = []
        for t in traces:
            item = {"seed":t["seed"],"family":t["family"]}
            for method in METHODS:
                counts = [dict(on_time=0,late=0,missing=0,sent=0) for _ in deadlines]
                for epoch,rates in enumerate(t["rates_mbps"]):
                    row=index[t["seed"],method,epoch]
                    assert row["rates"]==rates and row["sent"]==[rate*250 for rate in rates]
                    for i,(limit,out) in enumerate(zip(deadlines,counts)):
                        h={int(k):v for k,v in row["delay_ms_ceiling_histogram"][i].items()}
                        assert all(k>=0 and isinstance(v,int) and v>0 for k,v in h.items())
                        received=sum(h.values())
                        sent=row["sent"][i]
                        assert received==row["received"][i]<=sent
                        on_time=sum(v for k,v in h.items() if k<=limit)
                        out["on_time"]+=on_time
                        out["late"]+=received-on_time
                        out["missing"]+=sent-received
                        out["sent"]+=sent
                assert all(c["on_time"]+c["late"]+c["missing"]==c["sent"] for c in counts)
                rates=[100*c["on_time"]/c["sent"] for c in counts]
                rates.append(100*sum(c["on_time"] for c in counts)/sum(c["sent"] for c in counts))
                item[method]=dict(counts=counts,rates=rates)
            paired.append(item)
        means={method:[mean(row[method]["rates"][i] for row in paired) for i in range(3)] for method in METHODS}
        outputs[name]=dict(deadlines_ms=deadlines,paired=paired,means=means)
    return outputs


if __name__=="__main__":
    folder=Path("evidence")
    (folder/"deadlines.json").write_text(json.dumps(audit(folder),indent=2))
