"""Action-ledger queue projection and bounded-horizon dispersion surrogate.

No future exogenous capacity, arrival, or hidden queue is used. This controller
is a heuristic on the existing abstraction, not a probabilistic safety bound.
"""
import math
from baseline.simulate import allocate, DEADLINES


def fluid_service(q, weights, capacity):
    reserve=allocate(weights,max(0,int(capacity)))
    used=[min(q[s],reserve[s]) for s in range(2)]
    spare=capacity-sum(used)
    # Borrow by normalized residual workload. FIFO ages are not reported.
    for s in sorted(range(2),key=lambda s:(-(q[s]-used[s])/DEADLINES[s],s)):
        take=min(spare,max(0,q[s]-used[s]))
        used[s]+=take
        spare-=take
    return used


def project(reports,t,delay,ledger,pending):
    """Project each asynchronously observed stage using only known actions.

    Ledger has applied (extra, weights) for slots 0..t. Pending commands have
    immutable activation slots. Base capacity/arrival remain the last reports.
    Report queues are pre-service, and projected queues are pre-service too.
    """
    future=[]
    extra,weights=ledger[t]
    for u in range(t,t+delay):
        if u>t:
            for when,target,w in pending:
                if when==u:
                    extra,weights=target,w
        future.append((extra,weights))
    projected=[]
    for i,r in enumerate(reports):
        q=[float(x) for x in r['q']]
        for u in range(r['time'],t+delay):
            e,w=ledger[u] if u<=t else future[u-t]
            service=fluid_service(q,w[i],r['capacity']+e[i])
            q=[max(0,q[s]-service[s])+r['arrival'][s] for s in range(2)]
        projected.append(q)
    return projected


def solve_pipeline(reports,t,previous,delay,ledger,pending,margin_mode='bounded',project_actions=True):
    if project_actions:
        qhat=project(reports,t,delay,ledger,pending)
    else:
        qhat=[[max(0,r['q'][s]+(t+delay-r['time'])*(r['arrival'][s]-r['service'][s]))
               for s in range(2)] for r in reports]
    demand=[]
    for i,r in enumerate(reports):
        horizon=5 if margin_mode=='bounded' else t+delay-r['time']
        demand.append([qhat[i][s]+5*r['arrival'][s]+math.sqrt(horizon*r['variance'][s])+1 for s in range(2)])
    cache={}
    for i in range(3):
        for extra in ([0] if i==0 else range(4)):
            for k in range(1,20):
                quota=allocate([k/20,1-k/20],int(reports[i]['capacity'])+extra)
                cache[i,extra,k]=[demand[i][s]/max(.001,quota[s])/DEADLINES[s] for s in range(2)]
    best=None
    for x in range(4):
        for y in range(4):
            extra=[0,x,y]
            cost=sum(extra)+.25*sum(abs(extra[i]-previous[i]) for i in range(3))
            for k in range(1,20):
                ratios=[sum(cache[i,extra[i],k][s] for i in range(3)) for s in range(2)]
                worst=max(ratios)
                score=(0,cost,worst,sum(ratios),k) if worst<=1 else (1,worst,cost,sum(ratios),k)
                if best is None or score<best[0]:
                    best=(score,extra,k,ratios)
    _,extra,k,ratios=best
    return extra,[[k/20,1-k/20] for i in range(3)],dict(
        model_feasible=max(ratios)<=1,maximum_normalized_slack=max(0,max(ratios)-1),
        predicted_ratios=ratios,alpha=k/20)
