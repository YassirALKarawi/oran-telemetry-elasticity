"""Exploratory phase-duration sensitivity with a transition-aware comparator."""
import itertools,json,gzip,hashlib
from pathlib import Path
from experiment import instance

def evaluate(a,p,starts,phases):
    setup,ack,cutover=phases;n=len(p);h=a['horizon']
    ready=[s+setup for s in starts]
    copied=[ready[j]+a['duration'][j][p[j]] for j in range(n)]
    ends=[u+ack+cutover for u in copied]
    if max(ends)>h:return None
    for t in range(h):
        copying=[j for j in range(n) if ready[j]<=t<copied[j]]
        duplicated=[j for j in range(n) if starts[j]<=t<ends[j]]
        if sum(a['copy_rate'][j][p[j]] for j in copying)>a['copy_link']:return None
        if sum(a['cpu'][j] for j in duplicated)>a['temporary_cpu']:return None
        for k in range(2):
            cpu=sum(a['cpu'][j] for j in range(n) if p[j]==k and starts[j]<=t)
            # Reserve destination live bandwidth from readiness for cutover,
            # retaining the old source until the cutover completes.
            load=sum(a['traffic'][j] for j in range(n) if p[j]==k and copied[j]<=t)
            load+=sum(a['copy_rate'][j][k] for j in copying if p[j]==k)
            if cpu>a['capacity'][k] or load>a['link'][k]:return None
    cost=sum(a['cpu'][j]*(a['source_price']*ends[j]+a['price'][p[j]]*(a['lifetime']-starts[j])) for j in range(n))
    return dict(placement=list(p),starts=list(starts),ready=ready,copied=copied,ends=ends,cost=cost,makespan=max(ends))

def solve(a,phases):
    candidates=[]
    for p in itertools.product(range(2),repeat=3):
        if any(sum(a['cpu'][j] for j in range(3) if p[j]==k)>a['capacity'][k] or sum(a['traffic'][j] for j in range(3) if p[j]==k)>a['link'][k] for k in range(2)):continue
        best=None
        latest=[a['horizon']-sum(phases)-a['duration'][j][p[j]] for j in range(3)]
        for starts in itertools.product(*(range(v+1) for v in latest)):
            plan=evaluate(a,p,starts,phases)
            if plan and (best is None or (plan['cost'],plan['makespan'],plan['starts'])<(best['cost'],best['makespan'],best['starts'])):best=plan
        candidates.append(dict(steady=sum(a['cpu'][j]*a['price'][p[j]] for j in range(3)),plan=best))
    feasible=[c for c in candidates if c['plan']]
    if not feasible:return dict(joint=None,screened=None,sequential=None,candidates=candidates)
    key=lambda c:(c['plan']['cost'],c['plan']['makespan'],c['plan']['placement'])
    joint=min(feasible,key=key)['plan']
    screened=min(feasible,key=lambda c:(c['steady'],*key(c)))['plan']
    lowest=min(c['steady'] for c in candidates)
    tied=[c for c in feasible if c['steady']==lowest]
    sequential=min(tied,key=key)['plan'] if tied else None
    return dict(joint=joint,screened=screened,sequential=sequential,candidates=candidates)

if __name__=='__main__':
    root=Path(__file__).parent;rows=[]
    for phases in [(0,0,0),(1,1,1),(2,2,2)]:
        for seed in range(52000,52020):
            a=instance(seed);a['horizon']=12
            result=solve(a,phases)
            rows.append(dict(instance=a,phases=phases,**result))
        print('completed',phases,flush=True)
    summary=[]
    for phases in [(0,0,0),(1,1,1),(2,2,2)]:
        rr=[r for r in rows if tuple(r['phases'])==phases];pairs=[r for r in rr if r['screened']]
        summary.append(dict(phases=phases,n=len(rr),joint_feasible=sum(r['joint'] is not None for r in rr),screened_feasible=len(pairs),sequential_feasible=sum(r['sequential'] is not None for r in rr),strict_cost_improvements=sum(r['joint']['cost']<r['screened']['cost'] for r in pairs),mean_paired_saving=sum((r['screened']['cost']-r['joint']['cost'])/r['screened']['cost'] for r in pairs)/max(1,len(pairs))))
    out=dict(scope='Synthetic timing sensitivity, not measured timing or reproduction of MOVE-CU',code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),rows=rows,summary=summary)
    (root/'phased_results.json.gz').write_bytes(gzip.compress(json.dumps(out,indent=2).encode(),mtime=0))
    print(json.dumps(summary,indent=2))
