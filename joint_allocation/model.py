"""Joint unsplittable transport routing and processing placement.

Simulation abstraction: bandwidth/CPU are reserved quantities. Delay is a
deterministic path-plus-processing estimate, not a measured queueing delay.
"""
import itertools
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint

def options(a):
    out=[]
    for r in a['requests']:
        choices=[]
        for route in a['routes']:
            node=route[-1];edges=list(zip(route,route[1:]));keys=[f'{u}-{v}' for u,v in edges]
            delay=sum(a['links'][k]['delay'] for k in keys)+a['servers'][str(node)]['processing_delay']
            if delay>r['deadline']:continue
            cost=r['bandwidth']*sum(a['links'][k]['price'] for k in keys)+r['cpu']*a['servers'][str(node)]['price']
            choices.append(dict(route=route,node=str(node),links=keys,cost=cost,delay=delay))
        out.append(choices)
    return out

def verify(a,assignment):
    choices=options(a);link={k:0 for k in a['links']};cpu={k:0 for k in a['servers']};cost=0;served=0
    assert len(assignment)==len(a['requests'])
    for j,index in enumerate(assignment):
        if index is None:continue
        assert 0<=index<len(choices[j]);o=choices[j][index];r=a['requests'][j]
        assert o['delay']<=r['deadline'];served+=1;cost+=o['cost'];cpu[o['node']]+=r['cpu']
        for k in o['links']:link[k]+=r['bandwidth']
    assert all(link[k]<=a['links'][k]['capacity'] for k in link)
    assert all(cpu[k]<=a['servers'][k]['capacity'] for k in cpu)
    return dict(offered=len(assignment),served=served,rejected=len(assignment)-served,cost=cost,
                assignment=assignment,link_load=link,cpu_load=cpu)

def exact(a):
    opts=options(a);vars=[(j,k) for j,oo in enumerate(opts) for k in range(len(oo))]
    if not vars:return verify(a,[None]*len(opts))
    # This multiplier exceeds the maximum possible total assignment cost,
    # so admission count has strict priority over cost.
    big=1+sum(max([o['cost'] for o in oo],default=0) for oo in opts)
    rows=[];caps=[]
    for j in range(len(opts)):rows.append([int(jj==j) for jj,k in vars]);caps.append(1)
    for edge in a['links']:
        rows.append([a['requests'][j]['bandwidth'] if edge in opts[j][k]['links'] else 0 for j,k in vars]);caps.append(a['links'][edge]['capacity'])
    for node in a['servers']:
        rows.append([a['requests'][j]['cpu'] if node==opts[j][k]['node'] else 0 for j,k in vars]);caps.append(a['servers'][node]['capacity'])
    result=milp(np.array([opts[j][k]['cost']-big for j,k in vars]),integrality=np.ones(len(vars)),
                bounds=Bounds(0,1),constraints=LinearConstraint(np.array(rows),0,caps),
                options={'time_limit':30,'mip_rel_gap':0})
    if result.status!=0:raise RuntimeError('Exact optimum unverified: '+result.message)
    assignment=[None]*len(opts)
    for v,(j,k) in zip(result.x,vars):
        if v>.5:assignment[j]=k
    return verify(a,assignment)

def greedy(a,method='joint_greedy'):
    opts=options(a);assignment=[None]*len(opts)
    order=sorted(range(len(opts)),key=lambda j:(len(opts[j]),a['requests'][j]['bandwidth']+a['requests'][j]['cpu'],j))
    for j in order:
        indexes=sorted(range(len(opts[j])),key=lambda k:(opts[j][k]['cost'],k))
        if method=='placement_first' and indexes:
            # Choose the least-priced processing node before checking transport.
            node=min({o['node'] for o in opts[j]},key=lambda n:(a['servers'][n]['price'],n))
            indexes=[k for k in indexes if opts[j][k]['node']==node]
        for k in indexes:
            candidate=assignment.copy();candidate[j]=k
            try:verify(a,candidate)
            except AssertionError:continue
            assignment=candidate;break
    return verify(a,assignment)

def brute(a):
    best=None
    for assignment in itertools.product(*([None]+list(range(len(o))) for o in options(a))):
        try:r=verify(a,list(assignment))
        except AssertionError:continue
        if best is None or (-r['served'],r['cost'])<(-best['served'],best['cost']):best=r
    return best
