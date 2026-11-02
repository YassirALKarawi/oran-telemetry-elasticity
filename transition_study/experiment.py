"""Exact toy relocation/transition co-optimization. No O-RAN fidelity claim.

Three stateful services move from a source to one of two destinations. Each
destination has a private ingress link used by both live traffic and state
copy. A global migration link and temporary compute pool are also limited.
All options are enumerated. Baseline optimizes steady-state placement first,
then optimizes the transition exactly for that placement (not a weak order).
"""
import itertools,json,random,hashlib
from pathlib import Path

def schedules(instance,placement):
    n=len(placement);h=instance['horizon'];best=None
    for starts in itertools.product(range(h),repeat=n):
        ends=[starts[j]+instance['duration'][j][placement[j]] for j in range(n)]
        if max(ends)>h:continue
        valid=True
        for t in range(h):
            active=[j for j in range(n) if starts[j]<=t<ends[j]]
            if sum(instance['copy_rate'][j][placement[j]] for j in active)>instance['copy_link']:valid=False;break
            if sum(instance['cpu'][j] for j in active)>instance['temporary_cpu']:valid=False;break
            for k in range(2):
                placed=[j for j in range(n) if placement[j]==k]
                copying=[j for j in placed if j in active]
                completed=[j for j in placed if ends[j]<=t]
                cpu=sum(instance['cpu'][j] for j in copying+completed)
                traffic=sum(instance['copy_rate'][j][placement[j]] for j in copying)+sum(instance['traffic'][j] for j in completed)
                if cpu>instance['capacity'][k] or traffic>instance['link'][k]:valid=False;break
            if not valid:break
        if not valid:continue
        # Source occupancy persists until completion. Destination is allocated
        # from copy start, including temporary duplication during migration.
        destination=sum(instance['cpu'][j]*instance['price'][placement[j]]*(instance['lifetime']-starts[j]) for j in range(n))
        source=sum(instance['cpu'][j]*instance['source_price']*ends[j] for j in range(n))
        cost=destination+source
        score=(cost,max(ends),starts)
        if best is None or score<best[0]:best=(score,dict(placement=list(placement),starts=list(starts),ends=ends,cost=cost,makespan=max(ends)))
    return None if best is None else best[1]

def solve(instance):
    choices=[]
    for placement in itertools.product(range(2),repeat=len(instance['cpu'])):
        if any(sum(instance['cpu'][j] for j in range(len(placement)) if placement[j]==k)>instance['capacity'][k] or sum(instance['traffic'][j] for j in range(len(placement)) if placement[j]==k)>instance['link'][k] for k in range(2)):continue
        steady=sum(instance['cpu'][j]*instance['price'][placement[j]] for j in range(len(placement)))
        plan=schedules(instance,placement)
        choices.append(dict(steady_cost=steady,placement=list(placement),plan=plan))
    if not choices:return dict(baseline=None,joint=None,reason='no feasible final placement')
    minimum=min(c['steady_cost'] for c in choices)
    tied=[c['plan'] for c in choices if c['steady_cost']==minimum and c['plan'] is not None]
    baseline=min(tied,key=lambda p:(p['cost'],p['makespan'],p['placement'])) if tied else None
    feasible=[c['plan'] for c in choices if c['plan'] is not None]
    joint=min(feasible,key=lambda p:(p['cost'],p['makespan'],p['placement'])) if feasible else None
    if baseline is not None:assert joint['cost']<=baseline['cost']
    return dict(baseline=baseline,joint=joint,candidates=choices)

def instance(seed):
    r=random.Random(seed)
    rates=[[1,2] for _ in range(3)]
    size=[r.choice([2,3,4]) for _ in range(3)]
    return dict(seed=seed,horizon=8,lifetime=20,cpu=[r.choice([1,2]) for _ in range(3)],
        traffic=[r.choice([1,2]) for _ in range(3)],copy_rate=rates,state_size=size,
        duration=[[(size[j]+rate-1)//rate for rate in rates[j]] for j in range(3)],
        capacity=[4,4],link=[4,5],copy_link=3,temporary_cpu=3,price=[1,2],source_price=4)

if __name__=='__main__':
    root=Path(__file__).resolve().parent
    rows=[dict(instance=(ins:=instance(seed)),**solve(ins)) for seed in range(51000,51040)]
    pairs=[r for r in rows if r['baseline'] and r['joint']]
    out=dict(scope='Exploratory exact three-service toy model, not publication validation',
        protocol_sha256=hashlib.sha256((root/'PROTOCOL.md').read_bytes()).hexdigest(),
        rows=rows,summary=dict(instances=len(rows),paired_feasible=len(pairs),
            strict_improvements=sum(r['joint']['cost']<r['baseline']['cost'] for r in pairs),
            baseline_transition_infeasible=sum(r['baseline'] is None and r['joint'] is not None for r in rows),
            both_infeasible=sum(r['joint'] is None for r in rows),
            mean_paired_saving=sum((r['baseline']['cost']-r['joint']['cost'])/r['baseline']['cost'] for r in pairs)/max(1,len(pairs))))
    (root/'results.json').write_text(json.dumps(out,indent=2))
    print(json.dumps(out['summary'],indent=2))
