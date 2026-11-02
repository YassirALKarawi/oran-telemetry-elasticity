"""Exact finite-horizon admission/service reference, not an online controller.

Each packet needs one unit per stage, in strictly increasing slots. Inputs are
integer capacities known over this finite instance. Rejection is explicit.
No radio or deployment guarantee is inferred from this scheduling model.
"""
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix


def solve(packets, capacities, mandatory=(), lag=None, max_extra=0):
    """packets=(release,inclusive final deadline), capacities[stage][slot].

    Optional constant extra transport/compute capacity activates at slot lag.
    Lexicographically maximize admitted packets then minimize added unit-slots.
    mandatory indexes cannot be rejected. A returned certificate is checked.
    """
    raw=np.asarray(capacities)
    if raw.ndim != 2 or not np.all(np.isfinite(raw)) or np.any(raw<0) or np.any(raw!=np.floor(raw)):
        raise ValueError('Capacity must contain nonnegative integers')
    cap=raw.astype(int)
    stages,horizon=cap.shape
    n=len(packets)
    if n==0 or stages<1 or horizon<1: raise ValueError('Nonempty instance required')
    if any(r<0 or d<r or d>=horizon for r,d in packets): raise ValueError('Invalid packet window')
    if max_extra<0 or (max_extra and (lag is None or lag<0)): raise ValueError('Invalid actuation')
    mandatory=set(mandatory)
    if not mandatory.issubset(range(n)): raise ValueError('Invalid mandatory index')
    variables={}
    k=n
    for p,(r,d) in enumerate(packets):
        for i in range(stages):
            for t in range(r+i,d-(stages-1-i)+1):
                variables[p,i,t]=k;k+=1
    extra={i:k+j for j,i in enumerate(range(1,stages))} if max_extra else {}
    k+=len(extra)
    lower=np.zeros(k);upper=np.ones(k)
    for p in mandatory: lower[p]=1
    for v in extra.values(): upper[v]=max_extra
    rows=[];lo=[];hi=[]
    def add(coef,a,b):rows.append(coef);lo.append(a);hi.append(b)
    for p in range(n):
        for i in range(stages):
            coef={v:1 for (pp,ii,t),v in variables.items() if pp==p and ii==i};coef[p]=-1
            add(coef,0,0)
        for i in range(stages-1):
            for t in range(horizon):
                coef={v:1 for (pp,ii,tt),v in variables.items() if pp==p and ii==i+1 and tt<=t}
                coef.update({v:-1 for (pp,ii,tt),v in variables.items() if pp==p and ii==i and tt<t})
                if coef:add(coef,-np.inf,0)
    for i in range(stages):
        for t in range(horizon):
            coef={v:1 for (p,ii,tt),v in variables.items() if ii==i and tt==t}
            if i in extra and t>=lag:coef[extra[i]]=-1
            add(coef,-np.inf,int(cap[i,t]))
    matrix=lil_matrix((len(rows),k))
    for row,coef in enumerate(rows):
        for col,val in coef.items():matrix[row,col]=val
    constraint=LinearConstraint(matrix.tocsr(),lo,hi)
    cost=np.zeros(k);cost[:n]=-1
    first=milp(cost,integrality=np.ones(k),bounds=Bounds(lower,upper),constraints=constraint,
               options={'time_limit':60,'mip_rel_gap':0})
    if first.status==2:return {'feasible':False,'reason':'mandatory commitments infeasible'}
    if first.status!=0:raise RuntimeError('Optimal reference not established: '+first.message)
    admitted=int(round(sum(first.x[:n])))
    chosen=first
    if extra:
        count=np.zeros((1,k));count[0,:n]=1
        cost[:n]=0
        for v in extra.values():cost[v]=max(0,horizon-lag)
        chosen=milp(cost,integrality=np.ones(k),bounds=Bounds(lower,upper),
            constraints=[constraint,LinearConstraint(count,admitted,admitted)],
            options={'time_limit':60,'mip_rel_gap':0})
        if chosen.status!=0:raise RuntimeError('Secondary optimum not established')
    selected=[p for p in range(n) if chosen.x[p]>.5]
    assignments=[(p,i,t) for (p,i,t),v in variables.items() if chosen.x[v]>.5]
    expansion=[0]+[int(round(chosen.x[extra[i]])) if i in extra else 0 for i in range(1,stages)]
    result=dict(feasible=True,offered=n,admitted=admitted,rejected=n-admitted,
        timely_per_offered=admitted/max(1,n),selected=selected,assignments=assignments,
        expansion=expansion,extra_unit_slots=sum(expansion)*max(0,horizon-(lag or 0)),
        status='optimal finite-instance reference')
    check(packets,cap,result,mandatory,lag)
    return result


def check(packets,capacities,result,mandatory=(),lag=None):
    """Verify an explicit schedule without using the optimizer constraints."""
    cap=np.asarray(capacities);stages,horizon=cap.shape
    selected=set(result['selected']);assert set(mandatory)<=selected
    assert result['admitted']==len(selected) and result['rejected']==len(packets)-len(selected)
    usage=np.zeros_like(cap)
    for p in selected:
        times=[]
        for i in range(stages):
            slots=[t for pp,ii,t in result['assignments'] if pp==p and ii==i]
            assert len(slots)==1
            t=slots[0];assert 0<=t<horizon;usage[i,t]+=1;times.append(t)
        r,d=packets[p];assert r<=times[0] and times[-1]<=d
        assert all(a<b for a,b in zip(times,times[1:]))
    assert len(result['assignments'])==stages*len(selected)
    for i in range(stages):
        for t in range(horizon):
            extra=result['expansion'][i] if lag is not None and t>=lag else 0
            assert usage[i,t]<=cap[i,t]+extra
    return True
