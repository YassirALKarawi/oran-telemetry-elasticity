"""Post-hoc exploratory static-capacity frontier, not a confirmatory test."""
import gzip,json,random,statistics
from pathlib import Path
from online import ReservationController,execute_certificate
root=Path(__file__).resolve().parent;rows=[]
for seed in range(41000,41020):
    rng=random.Random(seed);h=24
    packets=[(r,min(h-1,r+rng.choice([5,9]))) for r in sorted(rng.randrange(14) for _ in range(36))]
    for x in range(3):
        for y in range(3):
            floors=(2,1+x,1+y);c=ReservationController(floors=floors,maximum=0)
            for ident,(r,d) in enumerate(packets):c.observe(ident,r,d)
            result=execute_certificate(c,lambda i,t:floors[i])
            rows.append(dict(seed=seed,extra=[x,y],charged_extra_unit_slots=24*(x+y),**result))
summaries=[]
for x in range(3):
    for y in range(3):
        rr=[r for r in rows if r['extra']==[x,y]]
        summaries.append(dict(extra=[x,y],cost=24*(x+y),timely_fraction=statistics.fmean(r['timely_per_offered'] for r in rr)))
out=dict(scope='Post-hoc nine-point static provisioning frontier on the same development traces. All extra resources active from slot zero.',runs=rows,summaries=summaries)
(root/'static_frontier.json.gz').write_bytes(gzip.compress(json.dumps(out,indent=2).encode(),mtime=0))
print(json.dumps(summaries,indent=2))
