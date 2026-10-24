"""Select stronger static comparators on calibration seeds, then lock evaluation.
No held-out outcome is used for policy or comparator selection.
"""
import json
import statistics as st
from pathlib import Path
from baseline.simulate import trace
from engine_static import run
from experiment import bootstrap_ci

CASES=[('nominal',3,.05),('bursty_transport',3,.05),
       ('bursty_compute',3,.05),('bursty_transport',9,.15)]
STATIC=[f'static_{x}_{y}' for x in range(4) for y in range(4)]
TARGET=.01
MEASURE=3000


def summarize(rows):
    return dict(violation=[st.fmean(r['violation'][s] for r in rows) for s in range(2)],
                cost=st.fmean(r['abstract_cost'] for r in rows),
                weighted=st.fmean(sum(r['violation'][s]*r['arrivals'][s] for s in range(2))/sum(r['arrivals']) for r in rows))


def main():
    root=Path(__file__).resolve().parent
    calibration,heldout,selections,summary,paired=[],[],[],[],[]
    for scenario,delay,loss in CASES:
        label=f'{scenario}_delay{delay}_loss{loss}'
        cal=[]
        for seed in range(4000,4005):
            events=trace(seed,3340,scenario)
            for name in STATIC+['elastic_cap3']:
                cal.append(dict(case=label,**run(events,name,seed=seed,measure=MEASURE,delay=delay,loss=loss)))
        means={name:summarize([r for r in cal if r['config']==name]) for name in STATIC+['elastic_cap3']}
        feasible=[n for n in STATIC if max(means[n]['violation'])<=TARGET]
        best=(min(feasible,key=lambda n:(means[n]['cost'],max(means[n]['violation']),n)) if feasible else
              min(STATIC,key=lambda n:(max(means[n]['violation']),means[n]['cost'],n)))
        affordable=[n for n in STATIC if means[n]['cost']<=means['elastic_cap3']['cost']]
        matched=min(affordable,key=lambda n:(means[n]['weighted'],max(means[n]['violation']),n))
        selections.append(dict(case=label,selected_static=best,calibration_target_met=bool(feasible),
                               budget_matched_static=matched,calibration_summaries=means))
        calibration.extend(cal)
        print(label+': comparators frozen '+best+' / '+matched,flush=True)
        for seed in range(5000,5020):
            events=trace(seed,3340,scenario)
            group=[]
            for role,name in [('dynamic','elastic_cap3'),('selected_static',best),
                              ('budget_static',matched),('unexpanded','static_0_0')]:
                group.append(dict(case=label,role=role,**run(events,name,seed=seed,measure=MEASURE,delay=delay,loss=loss)))
            for key in ('trace_hash','arrivals','requests','delivered'):
                assert all(r[key]==group[0][key] for r in group)
            heldout.extend(group)
        for role in ('dynamic','selected_static','budget_static','unexpanded'):
            rr=[r for r in heldout if r['case']==label and r['role']==role]
            summary.append(dict(case=label,role=role,config=rr[0]['config'],**summarize(rr)))
        new={r['seed']:r for r in heldout if r['case']==label and r['role']=='dynamic'}
        for role in ('selected_static','budget_static','unexpanded'):
            old={r['seed']:r for r in heldout if r['case']==label and r['role']==role}
            for metric,fn in [('class0',lambda r:r['violation'][0]),('class1',lambda r:r['violation'][1]),
                              ('cost',lambda r:r['abstract_cost'])]:
                diff=[fn(new[s])-fn(old[s]) for s in new]
                paired.append(dict(case=label,comparator=role,metric=metric,difference=st.fmean(diff),ci95=bootstrap_ci(diff)))
        print(label+': held-out evaluation complete',flush=True)
    result=dict(status='frozen_abstract_model_evaluation_not_validated_ORAN',
                calibration_seeds=[4000,4004],evaluation_seeds=[5000,5019],target=TARGET,
                measurement_slots=MEASURE,selections=selections,calibration_runs=calibration,
                heldout_runs=heldout,summaries=summary,paired_comparisons=paired)
    (root/'frozen_results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
