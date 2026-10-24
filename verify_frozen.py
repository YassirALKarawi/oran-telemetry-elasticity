"""Independent accounting, selection and regression checks for frozen results."""
import json
from pathlib import Path
from baseline.simulate import trace
from engine_static import run
from engine_v4 import run as previous_run

root=Path(__file__).resolve().parent
d=json.loads((root/'frozen_results.json').read_text())
assert len(d['calibration_runs'])==340
assert len(d['heldout_runs'])==320
assert {r['seed'] for r in d['calibration_runs']}.isdisjoint({r['seed'] for r in d['heldout_runs']})
for selection in d['selections']:
    means=selection['calibration_summaries']
    selected=selection['selected_static']
    if selection['calibration_target_met']:
        feasible=[n for n in means if n.startswith('static_') and max(means[n]['violation'])<=d['target']]
        assert selected==min(feasible,key=lambda n:(means[n]['cost'],max(means[n]['violation']),n))
    assert means[selection['budget_matched_static']]['cost']<=means['elastic_cap3']['cost']
    for seed in range(5000,5020):
        group=[r for r in d['heldout_runs'] if r['case']==selection['case'] and r['seed']==seed]
        assert len(group)==4
        for key in ('trace_hash','arrivals','requests','delivered'):
            assert all(r[key]==group[0][key] for r in group)
for r in d['calibration_runs']+d['heldout_runs']:
    assert abs(r['abstract_cost']-r['extra_service_unit_slots']-.25*r['activation_switching_units'])<1e-9
    assert all(0<=v<=1 for v in r['violation'])
for seed in (77,78,79):
    e=trace(seed,120,'nominal')
    for name,old in [('static_0_0','fixed'),('static_3_3','always_on')]:
        a=run(e,name,seed=seed,warmup=10,measure=60)
        b=previous_run(e,old,seed=seed,warmup=10,measure=60)
        a['config']=b['config']
        assert a==b
print('PASS: 660 runs; disjoint seed sets; static selection; event/report budgets; costs; six regression comparisons.')
