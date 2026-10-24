"""Frozen paper evaluation after development seeds 8000-8004.

The delay gate is selected before reading seeds 9000-9019. A gated run uses
preprovisioned calibrated capacity at/above 15 slots, not an instant switch.
"""
import hashlib
import json
import statistics as st
from pathlib import Path
from baseline.simulate import trace
from engine_static import run
from extension_evaluation import interval,sign_test

ROOT=Path(__file__).resolve().parent
CASES=[('nominal',3,.05,10,'static_0_0'),('bursty_transport',3,.05,10,'static_2_0'),
       ('bursty_compute',3,.05,10,'static_0_2'),('bursty_transport',9,.15,10,'static_2_0'),
       ('bursty_transport',3,.05,1,'static_2_0'),('bursty_transport',3,.05,25,'static_2_0'),
       ('bursty_transport',3,.05,50,'static_2_0'),('bursty_transport',3,.05,100,'static_2_0')]
METHODS=['legacy','pipeline','gated','margin_only','fixed']
GATE=15


def execute(events,method,fixed,seed,delay,loss,lag,audit_log=None):
    fallback=method=='fixed' or (method=='gated' and lag>=GATE)
    name=fixed if fallback else 'elastic_cap3'
    mode=None if method=='legacy' or fallback else ('margin_only' if method=='margin_only' else 'full')
    return run(events,name,seed=seed,delay=delay,loss=loss,activation_delay=lag,
               pipeline_mode=mode,audit_log=audit_log)


def main():
    checkpoint=ROOT/'paper_checkpoint.json'
    results=json.loads(checkpoint.read_text()) if checkpoint.exists() else []
    for scenario,delay,loss,lag,fixed in CASES:
        case=f'{scenario}_r{delay}_p{loss}_a{lag}'
        existing=[r for r in results if r['case']==case]
        if existing:
            assert len(existing)==100
            continue
        for seed in range(9000,9020):
            events=trace(seed,3340,scenario)
            group=[dict(case=case,method=method,lag=lag,
                        **execute(events,method,fixed,seed,delay,loss,lag)) for method in METHODS]
            for key in ('trace_hash','arrivals','requests','delivered'):
                assert all(r[key]==group[0][key] for r in group)
            if lag>=GATE:
                a=next(r for r in group if r['method']=='gated')
                b=next(r for r in group if r['method']=='fixed')
                assert {k:v for k,v in a.items() if k!='method'}=={k:v for k,v in b.items() if k!='method'}
            results.extend(group)
        (ROOT/'paper_checkpoint.json').write_text(json.dumps(results))
        print(case,'complete',len(results),flush=True)
    summaries=[]
    paired=[]
    for case in dict.fromkeys(r['case'] for r in results):
        groups={m:sorted([r for r in results if r['case']==case and r['method']==m],key=lambda x:x['seed']) for m in METHODS}
        for m,rr in groups.items():
            summaries.append(dict(case=case,method=m,lag=rr[0]['lag'],
                violation=[st.fmean(r['violation'][s] for r in rr) for s in (0,1)],
                ci=[interval([r['violation'][s] for r in rr]) for s in (0,1)],
                cost=st.fmean(r['abstract_cost'] for r in rr),cost_ci=interval([r['abstract_cost'] for r in rr])))
        for comparator in ('legacy','fixed'):
            for metric,get in [('class0',lambda r:r['violation'][0]),('class1',lambda r:r['violation'][1]),('cost',lambda r:r['abstract_cost'])]:
                dif=[get(a)-get(b) for a,b in zip(groups['gated'],groups[comparator])]
                paired.append(dict(case=case,comparator=comparator,metric=metric,
                    mean=st.fmean(dif),ci=interval(dif),**sign_test(dif)))
    running=0
    for rank,item in enumerate(sorted(paired,key=lambda x:x['p_raw'])):
        running=max(running,min(1,(len(paired)-rank)*item['p_raw']))
        item['p_holm']=running
    data=dict(status='abstract_service_chain_simulation',gate_slots=GATE,
              protocol_sha256=hashlib.sha256((ROOT/'PAPER_PROTOCOL.md').read_bytes()).hexdigest(),
              seeds=[9000,9019],runs=results,summaries=summaries,paired=paired)
    (ROOT/'paper_results.json').write_text(json.dumps(data,indent=2))
    print('COMPLETE',len(results),flush=True)


if __name__=='__main__':
    main()
