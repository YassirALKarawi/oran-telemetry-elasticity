"""Reconcile paper records, uncertainty and selected deterministic replays."""
import hashlib
import json
import math
import statistics as st
from pathlib import Path
from baseline.simulate import trace
from paper_evaluation import execute, CASES, METHODS
from extension_evaluation import interval, sign_test

ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'paper_results.json').read_text())
assert len(D['runs'])==800 and len(D['summaries'])==40 and len(D['paired'])==48
assert D['protocol_sha256']==hashlib.sha256((ROOT/'PAPER_PROTOCOL.md').read_bytes()).hexdigest()
for scenario,delay,loss,lag,fixed in CASES:
    case=f'{scenario}_r{delay}_p{loss}_a{lag}'
    for seed in range(9000,9020):
        rr=[r for r in D['runs'] if r['case']==case and r['seed']==seed]
        assert {r['method'] for r in rr}==set(METHODS) and len(rr)==5
        for k in ('trace_hash','requests','delivered','arrivals'):
            assert all(r[k]==rr[0][k] for r in rr)
        for r in rr:
            assert r['abstract_cost']==r['extra_service_unit_slots']+.25*r['activation_switching_units']
            for s in range(2):
                assert math.isclose(r['violation'][s],(r['late_completed'][s]+r['unfinished'][s])/r['arrivals'][s])
        a=next(r for r in rr if r['method']=='gated')
        b=next(r for r in rr if r['method']==('fixed' if lag>=15 else 'pipeline'))
        assert {k:v for k,v in a.items() if k!='method'}=={k:v for k,v in b.items() if k!='method'}
    for m in METHODS:
        rr=sorted([r for r in D['runs'] if r['case']==case and r['method']==m],key=lambda r:r['seed'])
        sr=next(r for r in D['summaries'] if r['case']==case and r['method']==m)
        assert sr['cost']==st.fmean(r['abstract_cost'] for r in rr)
        assert sr['cost_ci']==interval([r['abstract_cost'] for r in rr])
        for s in range(2):
            assert sr['violation'][s]==st.fmean(r['violation'][s] for r in rr)
            assert sr['ci'][s]==interval([r['violation'][s] for r in rr])
for p in D['paired']:
    a=sorted([r for r in D['runs'] if r['case']==p['case'] and r['method']=='gated'],key=lambda r:r['seed'])
    b=sorted([r for r in D['runs'] if r['case']==p['case'] and r['method']==p['comparator']],key=lambda r:r['seed'])
    get=(lambda r:r['abstract_cost']) if p['metric']=='cost' else (lambda r:r['violation'][int(p['metric'][-1])])
    dif=[get(x)-get(y) for x,y in zip(a,b)]
    assert p['mean']==st.fmean(dif) and p['ci']==interval(dif)
    assert all(p[k]==v for k,v in sign_test(dif).items())
last=0
for rank,p in enumerate(sorted(D['paired'],key=lambda p:p['p_raw'])):
    last=max(last,min(1,(48-rank)*p['p_raw']))
    assert p['p_holm']==last
replayed=0
for ix,m in [(0,'pipeline'),(1,'legacy'),(2,'pipeline'),(3,'margin_only'),(7,'pipeline'),(7,'gated')]:
    scenario,delay,loss,lag,fixed=CASES[ix]
    actual=execute(trace(9000,3340,scenario),m,fixed,9000,delay,loss,lag)
    saved=next(r for r in D['runs'] if r['case']==f'{scenario}_r{delay}_p{loss}_a{lag}' and r['method']==m and r['seed']==9000)
    assert actual=={k:v for k,v in saved.items() if k not in ('case','method','lag')}
    replayed+=1
print(json.dumps(dict(runs_checked=800,summaries_checked=40,paired_tests_checked=48,deterministic_replays=replayed,pass_all=True)))
