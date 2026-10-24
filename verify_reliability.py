"""Reconcile all frozen calibration/test records and replay one of each policy."""
import hashlib
import json
import math
import statistics as st
from pathlib import Path
from reliability_study import (CAL_SEEDS,TEST_SEEDS,CAL_CASES,TEST_CASES,GRIDS,EPS,DELTA,
                               execute,summarize,upper,interval)

ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'reliability_results.json').read_text())
C=json.loads((ROOT/'reliability_calibration.json').read_text())
S=json.loads((ROOT/'reliability_selection.json').read_text())
protocol=hashlib.sha256((ROOT/'RELIABILITY_PROTOCOL.md').read_bytes()).hexdigest()
assert all(v['protocol_sha256']==protocol for v in (D,C,S))
assert D['calibration_runs']==len(C['runs'])==336
assert D['test_runs']==len(D['runs'])==840
assert len(D['summaries'])==42 and len(D['paired'])==35
assert set(CAL_SEEDS).isdisjoint(TEST_SEEDS)
assert {r['seed'] for r in C['runs']}==set(CAL_SEEDS)
assert {r['seed'] for r in D['runs']}==set(TEST_SEEDS)
for score in S['scores']:
    rr=[r for r in C['runs'] if r['method']==score['method'] and r['param']==score['param']]
    assert len(rr)==12
    strata=[summarize([r for r in rr if r['case']==c]) for c in dict.fromkeys(r['case'] for r in rr)]
    assert score['strata']==strata
    assert score['eligible']==all(max(s['upper95'])<=EPS for s in strata)
for m in ('fixed','risk','hpa','dpp'):
    feasible=[s for s in S['scores'] if s['method']==m and s['eligible']]
    expected=min(feasible,key=lambda s:s['cost'])['param'] if feasible else None
    assert D['selected'][m]==S['selected'][m]==expected
for case in dict.fromkeys(r['case'] for r in D['runs']):
    for seed in TEST_SEEDS:
        rr=[r for r in D['runs'] if r['case']==case and r['seed']==seed]
        assert len(rr)==6 and len({r['method'] for r in rr})==6
        for k in ('trace_hash','requests','delivered','arrivals'):
            assert all(r[k]==rr[0][k] for r in rr)
        for r in rr:
            assert r['abstract_cost']==r['extra_service_unit_slots']+.25*r['activation_switching_units']
            for s in (0,1):
                assert math.isclose(r['violation'][s],(r['late_completed'][s]+r['unfinished'][s])/r['arrivals'][s])
    for m in D['parameters']:
        rr=[r for r in D['runs'] if r['case']==case and r['method']==m]
        actual=next(r for r in D['summaries'] if r['case']==case and r['method']==m)
        assert actual==dict(case=case,method=m,**summarize(rr))
    a=sorted([r for r in D['runs'] if r['case']==case and r['method']=='risk'],key=lambda r:r['seed'])
    for p in [p for p in D['paired'] if p['case']==case]:
        b=sorted([r for r in D['runs'] if r['case']==case and r['method']==p['comparator']],key=lambda r:r['seed'])
        cost=[x['abstract_cost']-y['abstract_cost'] for x,y in zip(a,b)]
        dif=[[x['violation'][s]-y['violation'][s] for x,y in zip(a,b)] for s in (0,1)]
        assert p['cost_difference']==st.fmean(cost) and p['cost_ci']==interval(cost)
        assert p['miss_difference']==[st.fmean(v) for v in dif]
        assert p['miss_upper95']==[upper(v) for v in dif]
        assert p['descriptive_noninferior']==all(upper(v)<=DELTA for v in dif)
replays=[]
for m,case in zip(D['parameters'],[TEST_CASES[0],TEST_CASES[6],TEST_CASES[1],TEST_CASES[2],TEST_CASES[3],TEST_CASES[5]]):
    actual=execute(TEST_SEEDS[0],case,m,D['parameters'][m])
    saved=next(r for r in D['runs'] if r['case']==actual['case'] and r['seed']==TEST_SEEDS[0] and r['method']==m)
    assert actual==saved
    replays.append([m,actual['case']])
print(json.dumps(dict(calibration=336,heldout=840,summaries=42,paired=35,replays=replays,pass_all=True)))
