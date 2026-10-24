"""Execute the locked protocol, with per-case checkpoints and raw results."""
import hashlib
import json
import math
import platform
import statistics as st
import time
from pathlib import Path
import numpy as np
from baseline.simulate import trace
from engine_static import run

ROOT=Path(__file__).resolve().parent
CASES=[('nominal',3,.05,'static_0_0'),('bursty_transport',3,.05,'static_2_0'),
       ('bursty_compute',3,.05,'static_0_2'),('bursty_transport',9,.15,'static_2_0')]
VARIANTS={'full':{},'round_robin':dict(telemetry_policy='periodic'),
          'oldest_first':dict(telemetry_policy='oldest'),
          'no_prediction':dict(use_prediction=False),'no_margin':dict(use_margin=False),
          'selected_fixed':{}}


def interval(values):
    a=np.asarray(values,dtype=float)
    rng=np.random.default_rng(81028)
    sample=a[rng.integers(0,len(a),size=(10000,len(a)))].mean(axis=1)
    return [float(x) for x in np.quantile(sample,[.025,.975])]


def sign_test(values):
    positive=sum(v>0 for v in values)
    negative=sum(v<0 for v in values)
    n=positive+negative
    p=min(1.,2*sum(math.comb(n,k) for k in range(min(positive,negative)+1))/2**n) if n else 1.
    return dict(p_raw=p,positive=positive,negative=negative,ties=len(values)-n)


def summarize(rows):
    return dict(n=len(rows),violation=[st.fmean(r['violation'][s] for r in rows) for s in range(2)],
                violation_ci95=[interval([r['violation'][s] for r in rows]) for s in range(2)],
                cost=st.fmean(r['abstract_cost'] for r in rows),cost_ci95=interval([r['abstract_cost'] for r in rows]),
                zero_miss_seed_count=[sum(r['violation'][s]==0 for r in rows) for s in range(2)],
                total_measured_packets=[sum(r['arrivals'][s] for r in rows) for s in range(2)])


def main():
    started=time.time()
    raw=[]
    protocol_hash=hashlib.sha256((ROOT/'EXTENSION_PROTOCOL.md').read_bytes()).hexdigest()
    for scenario,delay,loss,fixed in CASES:
        case=f'{scenario}_delay{delay}_loss{loss}'
        for seed in range(6000,6020):
            events=trace(seed,3340,scenario)
            group=[]
            for variant,kwargs in VARIANTS.items():
                result=run(events,fixed if variant=='selected_fixed' else 'elastic_cap3',seed=seed,
                           delay=delay,loss=loss,**kwargs)
                group.append(dict(case=case,variant=variant,activation_delay=10,**result))
            for key in ('trace_hash','arrivals','requests','delivered'):
                assert all(r[key]==group[0][key] for r in group)
            raw.extend(group)
        (ROOT/'extension_checkpoint.json').write_text(json.dumps(raw))
        print(f'Primary: {case} complete ({len(raw)} runs)',flush=True)
    sensitivity=[]
    for lag in (1,5,10,25,50,100):
        for seed in range(7000,7010):
            events=trace(seed,3340,'bursty_transport')
            for variant,name in [('full','elastic_cap3'),('selected_fixed','static_2_0')]:
                sensitivity.append(dict(activation_delay=lag,variant=variant,
                    **run(events,name,seed=seed,activation_delay=lag)))
        print(f'Sensitivity: lag {lag} complete',flush=True)
    summaries=[]
    paired=[]
    ablations=[]
    for case in dict.fromkeys(r['case'] for r in raw):
        group={v:[r for r in raw if r['case']==case and r['variant']==v] for v in VARIANTS}
        for v,rr in group.items():
            summaries.append(dict(case=case,variant=v,**summarize(rr)))
        for metric,get in [('class0',lambda r:r['violation'][0]),('class1',lambda r:r['violation'][1]),
                           ('cost',lambda r:r['abstract_cost'])]:
            differences=[get(a)-get(b) for a,b in zip(group['full'],group['selected_fixed'])]
            paired.append(dict(case=case,metric=metric,difference=st.fmean(differences),
                               ci95=interval(differences),**sign_test(differences)))
        for v in ('round_robin','oldest_first','no_prediction','no_margin'):
            ablations.append(dict(case=case,variant=v,
                cost_change=st.fmean(a['abstract_cost']-b['abstract_cost'] for a,b in zip(group[v],group['full'])),
                miss_change=[st.fmean(a['violation'][s]-b['violation'][s] for a,b in zip(group[v],group['full'])) for s in range(2)]))
    running=0.
    for rank,item in enumerate(sorted(paired,key=lambda x:x['p_raw'])):
        running=max(running,min(1.,(len(paired)-rank)*item['p_raw']))
        item['p_holm']=running
    sens_summary=[dict(activation_delay=lag,variant=v,
                      **summarize([r for r in sensitivity if r['activation_delay']==lag and r['variant']==v]))
                  for lag in (1,5,10,25,50,100) for v in ('full','selected_fixed')]
    result=dict(status='verified_abstract_model_not_physical_ORAN_validation',
                protocol_sha256=protocol_hash,python=platform.python_version(),numpy=np.__version__,
                elapsed_seconds=time.time()-started,primary_runs=raw,sensitivity_runs=sensitivity,
                summaries=summaries,sensitivity_summaries=sens_summary,paired=paired,ablations=ablations,
                zero_miss_seed_probability_upper95=1-.05**(1/20))
    (ROOT/'extension_results.json').write_text(json.dumps(result,indent=2))
    print(f'COMPLETE: {len(raw)+len(sensitivity)} runs in {result["elapsed_seconds"]:.1f}s',flush=True)


if __name__=='__main__':
    main()
