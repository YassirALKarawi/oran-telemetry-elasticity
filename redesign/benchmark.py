"""Synthetic capability benchmark. Full future knowledge, not online performance."""
import hashlib,json,random,time
from pathlib import Path
from reference import solve

root=Path(__file__).resolve().parent
rows=[]
for seed in range(31000,31020):
    rng=random.Random(seed);h=18
    packets=[(r,min(h-1,r+rng.choice([5,9]))) for r in sorted(rng.randrange(10) for _ in range(24))]
    cap=[[rng.choice([1,2,2]) for _ in range(h)], [rng.choice([0,1,1]) for _ in range(h)], [1]*h]
    previous=25
    for lag in [0,1,3,6,12,18]:
        start=time.perf_counter();result=solve(packets,cap,lag=lag,max_extra=2)
        elapsed=time.perf_counter()-start
        assert result['admitted']<=previous
        previous=result['admitted']
        rows.append(dict(seed=seed,lag=lag,packets=packets,capacities=cap,elapsed_seconds=elapsed,**result))
    print('completed',seed,flush=True)
out={'interpretation':'Offline optimum on small synthetic instances. No O-RAN empirical validation or online superiority claim.',
     'code_sha256':hashlib.sha256((root/'reference.py').read_bytes()).hexdigest(),'runs':rows}
(root/'reference_results.json').write_text(json.dumps(out,indent=2))
for lag in [0,1,3,6,12,18]:
    rr=[r for r in rows if r['lag']==lag]
    print(lag,sum(r['admitted'] for r in rr)/480,sum(r['extra_unit_slots'] for r in rr)/20)
