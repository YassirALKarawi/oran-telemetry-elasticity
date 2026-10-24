"""Frozen reliability-screened comparison and distribution-shift evaluation.

Published-method adaptations are labelled adaptations, not reproduced systems.
Only calibration records select parameters. Every held-out result is retained.
"""
import hashlib
import json
import math
import random
import statistics as st
import time
from pathlib import Path
import numpy as np
from baseline.simulate import trace,allocate,DEADLINES
from engine_static import run
from pipeline_control import project
from extension_evaluation import interval

ROOT=Path(__file__).resolve().parent
CAL_SEEDS=list(range(12000,12006))
TEST_SEEDS=list(range(13000,13020))
EPS=.001  # 0.1% absolute mean-miss target, not a certified chance constraint.
DELTA=.001  # 0.1 percentage-point paired noninferiority margin.
CAL_CASES=[('periodic',3,.05,10),('periodic',9,.15,10)]
TEST_CASES=[('periodic',3,.05,10),('markov',3,.05,10),('compound',3,.05,10),
            ('compute',3,.05,10),('periodic',9,.15,10),('periodic',3,.05,50),
            ('jitter',3,.05,10)]
GRIDS={'risk':[.25,.5,.75,1.0],'hpa':[.55,.7,.85,.95],'dpp':[.1,.3,1.,3.]}

def workload(seed,kind):
    events=trace(seed,3340,'bursty_compute' if kind=='compute' else 'bursty_transport')
    if kind in ('periodic','compute','jitter'): return events
    rng=random.Random(seed+900000)
    high=False
    out=[]
    for t,(arr,cap) in enumerate(events):
        cap=list(cap)
        if high:
            if rng.random()<.02: high=False
        elif rng.random()<.005: high=True
        rates=(1.8,3.8) if high else (.9,2.1)
        aa=[]
        for rate in rates:
            # Compound Poisson: integer batches of 3 with the same conditional mean.
            batch=3 if kind=='compound' else 1
            product=1.;n=0
            while product>math.exp(-rate/batch): product*=rng.random();n+=1
            aa.append(batch*(n-1))
        cap[1]=3 if high else 5+rng.choice((-1,0,0,1))
        out.append((aa,cap))
    return out

def schedule(seed,kind,lag):
    if kind!='jitter': return None
    rng=random.Random(seed+800000)
    return [rng.choice([1,5,10,25,50]) for _ in range(668)]

def upper(values):
    """One-sided percentile bootstrap bound on the seed mean."""
    a=np.asarray(values,dtype=float)
    rng=np.random.default_rng(221026)
    means=a[rng.integers(0,len(a),(10000,len(a)))].mean(axis=1)
    return float(np.quantile(means,.95))

def grid(reports,t,previous,lag,ledger,pending,eta=1.,ledger_on=True,mode='risk',price=1.,forced=None):
    if ledger_on:
        q=project(reports,t,lag,ledger,pending)
    else:
        q=[[max(0,r['q'][s]+(t+lag-r['time'])*(r['arrival'][s]-r['service'][s])) for s in range(2)] for r in reports]
    demand=[[q[i][s]+5*r['arrival'][s]+math.sqrt(5*r['variance'][s])+1 for s in range(2)] for i,r in enumerate(reports)]
    extras=[forced] if forced is not None else [(0,x,y) for x in range(4) for y in range(4)]
    cache={}
    for i in range(3):
        for x in sorted(set(e[i] for e in extras)):
            for k in range(1,20):
                g=allocate([k/20,1-k/20],int(reports[i]['capacity'])+x)
                ratios=[demand[i][s]/max(.001,g[s])/DEADLINES[s]/eta for s in range(2)]
                benefit=sum((q[i][s]+5*reports[i]['arrival'][s])/DEADLINES[s]*min(demand[i][s],g[s]) for s in range(2))
                cache[i,x,k]=(ratios,benefit)
    best=None
    for e in extras:
        cost=sum(e)+.25*sum(abs(e[i]-previous[i]) for i in range(3))
        for k in range(1,20):
            ratios=[sum(cache[i,e[i],k][0][s] for i in range(3)) for s in range(2)]
            worst=max(ratios)
            if mode=='dpp':
                score=(price*cost-sum(cache[i,e[i],k][1] for i in range(3)),cost,k)
            else:
                score=(0,cost,worst,sum(ratios),k) if worst<=1 else (1,worst,cost,sum(ratios),k)
            if best is None or score<best[0]: best=(score,e,k,ratios)
    _,e,k,ratios=best
    return list(e),[[k/20,1-k/20] for _ in range(3)],dict(model_feasible=max(ratios)<=1,
        maximum_normalized_slack=max(0,max(ratios)-1),predicted_ratios=ratios,alpha=k/20)

class Controller:
    def __init__(self,method,param): self.method=method;self.param=param;self.history=[]
    def __call__(self,reports,t,previous,lag,ledger,pending):
        if self.method in ('risk','uncalibrated','no_ledger'):
            return grid(reports,t,previous,lag,ledger,pending,eta=self.param,ledger_on=self.method!='no_ledger')
        if self.method=='dpp':
            return grid(reports,t,previous,lag,ledger,pending,ledger_on=False,mode='dpp',price=self.param)
        # HPA-inspired target-utilization sizing with a 20-slot downscale window.
        target=[0]+[max(0,min(3,math.ceil((sum(r['arrival'])+sum(r['q'])/5)/self.param)-int(r['capacity']))) for r in reports[1:]]
        self.history.append((t,target))
        self.history=[(u,x) for u,x in self.history if t-u<20]
        target=[max(x[i] for _,x in self.history) for i in range(3)]
        # A common share optimizer avoids conflating capacity and share controls.
        return grid(reports,t,previous,lag,ledger,pending,ledger_on=False,forced=tuple(target))

def execute(seed,case,method,param):
    kind,r,p,lag=case
    events=workload(seed,kind)
    sched=schedule(seed,kind,lag)
    if method=='fixed':
        x,y=param
        if kind=='compute': x,y=y,x
        result=run(events,f'static_{x}_{y}',seed=seed,delay=r,loss=p,activation_delay=lag,activation_schedule=sched)
    else:
        result=run(events,'elastic_cap3',seed=seed,delay=r,loss=p,activation_delay=lag,
                   controller=Controller(method,param),activation_schedule=sched)
    return dict(case=f'{kind}_r{r}_p{p}_a{lag}',method=method,param=param,**result)

def summarize(rr):
    return dict(n=len(rr),cost=st.fmean(r['abstract_cost'] for r in rr),cost_ci=interval([r['abstract_cost'] for r in rr]),
        violation=[st.fmean(r['violation'][s] for r in rr) for s in range(2)],
        ci=[interval([r['violation'][s] for r in rr]) for s in range(2)],
        upper95=[upper([r['violation'][s] for r in rr]) for s in range(2)])

def main():
    started=time.time()
    protocol=hashlib.sha256((ROOT/'RELIABILITY_PROTOCOL.md').read_bytes()).hexdigest()
    calibration=[]
    configs=[('fixed',[x,y]) for x in range(4) for y in range(4)]
    configs += [(m,p) for m,params in GRIDS.items() for p in params]
    checkpoint=ROOT/'reliability_calibration.json'
    if checkpoint.exists():
        saved=json.loads(checkpoint.read_text());assert saved['protocol_sha256']==protocol;calibration=saved['runs']
    for method,param in configs:
        if any(r['method']==method and r['param']==param for r in calibration): continue
        group=[execute(seed,case,method,param) for case in CAL_CASES for seed in CAL_SEEDS]
        calibration.extend(group)
        checkpoint.write_text(json.dumps(dict(protocol_sha256=protocol,runs=calibration)))
        print('CAL',method,param,summarize(group)['violation'],flush=True)
    # Each calibration stratum must pass separately, not merely the pooled mean.
    scores=[]
    for method,param in configs:
        rr=[r for r in calibration if r['method']==method and r['param']==param]
        strata=[summarize([r for r in rr if r['case']==c]) for c in dict.fromkeys(r['case'] for r in rr)]
        scores.append(dict(method=method,param=param,cost=st.fmean(r['abstract_cost'] for r in rr),
                           eligible=all(max(r['upper95'])<=EPS for r in strata),strata=strata))
    selected={}
    for m in ['fixed','risk','hpa','dpp']:
        candidates=[r for r in scores if r['method']==m and r['eligible']]
        selected[m]=min(candidates,key=lambda r:r['cost'])['param'] if candidates else None
    # Prespecified failure rule: report calibration failure and use the most conservative
    # candidate as diagnostic only, never describe it as eligible.
    fallback={'fixed':[3,3],'risk':.25,'hpa':.55,'dpp':.1}
    parameters={m:selected[m] if selected[m] is not None else fallback[m] for m in selected}
    selection=dict(protocol_sha256=protocol,selected=selected,parameters=parameters,scores=scores)
    (ROOT/'reliability_selection.json').write_text(json.dumps(selection,indent=2))
    print('LOCKED',parameters,flush=True)
    parameters.update(uncalibrated=1.,no_ledger=parameters['risk'])
    runs=[]
    checkpoint=ROOT/'reliability_test_checkpoint.json'
    if checkpoint.exists():
        saved=json.loads(checkpoint.read_text());assert saved['protocol_sha256']==protocol;runs=saved['runs']
    for case in TEST_CASES:
        key=f'{case[0]}_r{case[1]}_p{case[2]}_a{case[3]}'
        if any(r['case']==key for r in runs): continue
        for seed in TEST_SEEDS:
            group=[execute(seed,case,m,p) for m,p in parameters.items()]
            for k in ['trace_hash','arrivals','requests','delivered']:
                assert all(r[k]==group[0][k] for r in group)
            runs.extend(group)
        checkpoint.write_text(json.dumps(dict(protocol_sha256=protocol,runs=runs)))
        print('TEST',key,'done',len(runs),flush=True)
    summaries=[];paired=[]
    for case in dict.fromkeys(r['case'] for r in runs):
        groups={m:sorted([r for r in runs if r['case']==case and r['method']==m],key=lambda r:r['seed']) for m in parameters}
        for m,rr in groups.items(): summaries.append(dict(case=case,method=m,**summarize(rr)))
        for m in ['fixed','hpa','dpp','uncalibrated','no_ledger']:
            difcost=[a['abstract_cost']-b['abstract_cost'] for a,b in zip(groups['risk'],groups[m])]
            difmiss=[[a['violation'][s]-b['violation'][s] for a,b in zip(groups['risk'],groups[m])] for s in range(2)]
            paired.append(dict(case=case,comparator=m,cost_difference=st.fmean(difcost),cost_ci=interval(difcost),
                miss_difference=[st.fmean(d) for d in difmiss],miss_upper95=[upper(d) for d in difmiss],
                descriptive_noninferior=all(upper(d)<=DELTA for d in difmiss)))
    out=dict(protocol_sha256=protocol,calibration_runs=len(calibration),test_runs=len(runs),
             parameters=parameters,selected=selected,runs=runs,summaries=summaries,paired=paired,
             elapsed_seconds=time.time()-started)
    (ROOT/'reliability_results.json').write_text(json.dumps(out,indent=2))
    print('COMPLETE',len(runs),'runs',time.time()-started,flush=True)

if __name__=='__main__': main()
