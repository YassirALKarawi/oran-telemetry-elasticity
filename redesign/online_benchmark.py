"""Prespecified synthetic causal comparison, no tuning or empirical claims."""
import gzip,hashlib,json,random,time,statistics
from pathlib import Path
from online import ReservationController,execute_certificate
from reference import solve

root=Path(__file__).resolve().parent
rows=[]
for seed in range(41000,41020):
    rng=random.Random(seed);h=24;floors=(2,1,1)
    packets=[(r,min(h-1,r+rng.choice([5,9]))) for r in sorted(rng.randrange(14) for _ in range(36))]
    digest=hashlib.sha256(json.dumps(packets).encode()).hexdigest()
    for lag in (1,3,6,12):
        upper=solve(packets,[[v]*h for v in floors],lag=lag,max_extra=2)
        for method in ('causal_leases','no_expansion','always_on'):
            cf=floors if method!='always_on' else (2,3,3)
            c=ReservationController(floors=cf,lag=lag,maximum=2 if method=='causal_leases' else 0)
            start=time.perf_counter()
            for ident,(r,d) in enumerate(packets):c.observe(ident,r,d)
            seconds=time.perf_counter()-start
            result=execute_certificate(c,lambda i,t:cf[i])
            if method!='always_on':assert result['timely']<=upper['admitted']
            assert result['late_or_failed_admitted']==0
            cost=result['extra_unit_slots'] if method!='always_on' else 4*h
            rows.append(dict(seed=seed,lag=lag,method=method,trace_sha256=digest,
                decision_seconds=seconds,charged_extra_unit_slots=cost,
                offline_upper_admitted=upper['admitted'],**result))
    print('completed',seed,flush=True)
summary=[]
for lag in (1,3,6,12):
    for method in ('causal_leases','no_expansion','always_on'):
        rr=[r for r in rows if r['lag']==lag and r['method']==method]
        summary.append(dict(lag=lag,method=method,n=len(rr),
            timely_fraction=statistics.fmean(r['timely_per_offered'] for r in rr),
            rejection_fraction=statistics.fmean(r['rejected_per_offered'] for r in rr),
            cost=statistics.fmean(r['charged_extra_unit_slots'] for r in rr),
            offline_upper_fraction=statistics.fmean(r['offline_upper_admitted']/r['offered'] for r in rr),
            mean_decision_ms=1000*statistics.fmean(r['decision_seconds']/r['offered'] for r in rr)))
out=dict(scope='Synthetic three-stage unit-job model with deterministic contractual service floors. Offline bound has future information. Always-on starts fully provisioned and is not cost-matched.',
    code_sha256=hashlib.sha256((root/'online.py').read_bytes()).hexdigest(),runs=rows,summaries=summary)
(root/'online_results.json').write_text(json.dumps(out,indent=2))
(root/'online_results.json.gz').write_bytes(gzip.compress((root/'online_results.json').read_bytes(),mtime=0))
print(json.dumps(summary,indent=2))
