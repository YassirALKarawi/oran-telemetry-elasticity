"""Check age-bin equations and deadline cuts against independent packet runs."""
import json
import math
import hashlib
from pathlib import Path
from collections import defaultdict
from baseline.simulate import allocate, DEADLINES
from engine_static import run
from reliability_study import workload, schedule, Controller

ROOT=Path(__file__).resolve().parent
saved=json.loads((ROOT/'reliability_results.json').read_text())
checks=[]
for kind,lag in [('periodic',10),('periodic',50),('jitter',10)]:
    for method in ['fixed','risk']:
        seed=13000
        events=workload(seed,kind)
        delays=schedule(seed,kind,lag)
        audit=[];issued=[]
        policy=Controller('risk',.75)
        def capture(reports,t,previous,L,ledger,pending):
            answer=policy(reports,t,previous,L,ledger,pending)
            issued.append((t,t+L,list(answer[0])))
            return answer
        got=run(events,'static_2_0' if method=='fixed' else 'elastic_cap3',
                seed=seed,delay=3,loss=.05,activation_delay=lag,activation_schedule=delays,
                controller=capture if method=='risk' else None,audit_log=audit)
        case=f'{kind}_r3_p0.05_a{lag}'
        expected=next(r for r in saved['runs'] if r['case']==case and r['method']==method and r['seed']==seed)
        for key in got: assert got[key]==expected[key],(case,method,key)
        # Sparse birth cohorts are an age-bin representation: age = time - birth.
        bins=[[defaultdict(int) for _ in range(2)] for _ in range(3)]
        admitted=[defaultdict(int) for _ in range(2)]
        ontime=[defaultdict(int) for _ in range(2)]
        pastlate=[defaultdict(int) for _ in range(2)]
        snapshots=[];backlog=0;max_irrecoverable=[0,0]
        for t,(arrivals,_) in enumerate(events):
            for s in range(2):
                bins[0][s][t]+=arrivals[s]
                if 300<=t<3300: admitted[s][t]+=arrivals[s]
            for s in range(2):
                irrecoverable=sum(n for i in range(3) for b,n in bins[i][s].items()
                                  if 300<=b<3300 and DEADLINES[s]-(t-b)-(3-i)<0)
                max_irrecoverable[s]=max(max_irrecoverable[s],irrecoverable)
            if t%200==0:
                d=min(t+39,len(events)-1)
                groups=[];demands=[]
                for i in range(3):
                    demands.append(sum(n for j in range(i+1) for s in range(2) for b,n in bins[j][s].items()
                                       if 300<=b<3300 and b+DEADLINES[s]-1<=d))
                births=[{b for j in range(3) for b,n in bins[j][s].items()
                         if n and 300<=b<3300 and b+DEADLINES[s]-1<=d} for s in range(2)]
                prior=sum(pastlate[s][b] for s in range(2) for b in births[s])
                snapshots.append((t,d,demands,births,prior))
            departures=[[defaultdict(int) for _ in range(2)] for _ in range(3)]
            for i in range(3):
                capacity=audit[t]['capacities'][i]
                reserved=allocate(audit[t]['weights'][i],capacity)
                used=0
                def take(s,n):
                    for b in sorted(bins[i][s]):
                        k=min(n,bins[i][s][b])
                        if k:
                            departures[i][s][b]+=k;bins[i][s][b]-=k;n-=k
                        if n==0: break
                for s in range(2):
                    n=min(reserved[s],sum(bins[i][s].values()))
                    take(s,n);used+=n
                while used<capacity:
                    heads=[(min(b for b,n in bins[i][s].items() if n)+DEADLINES[s],s)
                           for s in range(2) if any(bins[i][s].values())]
                    if not heads: break
                    _,s=min(heads);take(s,1);used+=1
            # Simultaneous transition ensures an upstream departure is unavailable
            # for downstream service until the next slot.
            for i in range(3):
                for s in range(2):
                    for b,n in departures[i][s].items():
                        if i<2: bins[i+1][s][b]+=n
                        elif 300<=b<3300:
                            (ontime if t-b+1<=DEADLINES[s] else pastlate)[s][b]+=n
                    bins[i][s]=defaultdict(int,{b:n for b,n in bins[i][s].items() if n})
            if 300<=t<3300: backlog+=sum(sum(q.values()) for stage in bins for q in stage)
        for s in range(2):
            n=sum(admitted[s].values());hit=sum(ontime[s].values())
            value=1-hit/n if n else 0
            assert max_irrecoverable[s]<=n-hit
            assert math.isclose(value,got['violation'][s],abs_tol=1e-12)
        assert math.isclose(backlog/3000,got['mean_backlog'],abs_tol=1e-12)
        for t,d,demands,births,prior in snapshots:
            miss=sum(admitted[s][b]-ontime[s][b] for s in range(2) for b in births[s])-prior
            for i in range(3):
                end=d-(2-i)
                cap=sum(audit[u]['capacities'][i] for u in range(t,end+1))
                assert miss>=max(0,demands[i]-cap)
        if method=='risk':
            active=[0,0,0];switch=0
            for t in range(len(events)):
                for k,(_,d,x) in enumerate(issued):
                    if d==t:
                        switch+=sum(abs(a-b) for a,b in zip(active,x));active=x
                eligible=[(d,k,x) for k,(_,d,x) in enumerate(issued) if d<=t]
                selected=max(eligible,key=lambda r:(r[0],r[1]))[2] if eligible else [0,0,0]
                assert active==selected
                assert [events[t][1][i]+active[i] for i in range(3)]==audit[t]['capacities']
            assert switch==got['activation_switching_units']
            if kind!='jitter':
                for t,d,_,_,_ in snapshots:
                    for i in range(3):
                        envelope=0
                        for u in range(t,d-(2-i)+1):
                            known=[(at,k,x) for k,(issued_at,at,x) in enumerate(issued) if issued_at<t and at<=u]
                            pending_extra=max(known,key=lambda v:(v[0],v[1]))[2][i] if known else 0
                            envelope+=events[u][1][i]+(pending_extra if u<t+lag else (0 if i==0 else 3))
                        actual=sum(audit[u]['capacities'][i] for u in range(t,d-(2-i)+1))
                        assert actual<=envelope
        checks.append(dict(case=case,method=method,slots=len(events),deadline_cuts=3*len(snapshots),passed=True))
receipt=dict(checks=checks,source_sha256=hashlib.sha256((ROOT/'reliability_results.json').read_bytes()).hexdigest(),
             unchanged_frozen_records=True,age_accounting=True,command_order=True,deadline_cuts=True,structural_slack_bound=True)
(ROOT/'advanced_model_verification.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt))
