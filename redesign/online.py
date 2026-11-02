"""Causal immutable service reservations with delayed finite capacity leases.

Only arrivals already observed and contractual service floors are available.
One unit of work per stage. A lease is a modeled resource commitment, not an
implemented O-RAN command. The guarantee is conditional on service floors.
"""
from itertools import combinations


class ReservationController:
    def __init__(self, floors=(2,1,1), lag=3, maximum=2, minimum_lease=5):
        if len(floors)!=3 or any(int(x)!=x or x<0 for x in floors):raise ValueError('Three integer floors required')
        if lag<0 or maximum<0 or minimum_lease<1:raise ValueError('Invalid lease parameters')
        self.floors=tuple(floors);self.lag=lag;self.maximum=maximum;self.minimum_lease=minimum_lease
        self.usage={};self.leases=[];self.accepted=[];self.rejected=[];self.last_arrival=-1

    def extra(self,i,t):return sum(stage==i and start<=t<end for stage,start,end in self.leases)

    def observe(self,ident,release,deadline):
        if release<self.last_arrival:raise ValueError('Arrivals must be observed in causal order')
        self.last_arrival=release
        best=None
        for slots in combinations(range(release,deadline+1),3):
            proposed=[];valid=True
            for i,u in enumerate(slots):
                if self.usage.get((i,u),0)<self.floors[i]+self.extra(i,u):continue
                if i==0 or u<release+self.lag:valid=False;break
                start=release+self.lag;end=max(start+self.minimum_lease,u+1)
                if any(self.extra(i,v)>=self.maximum for v in range(start,end)):valid=False;break
                proposed.append((i,start,end))
            if valid:
                score=(sum(e-s for i,s,e in proposed),slots[-1],slots)
                if best is None or score<best[0]:best=(score,slots,proposed)
        if best is None:self.rejected.append(ident);return False
        _,slots,leases=best
        self.leases.extend(leases)
        for i,u in enumerate(slots):self.usage[i,u]=self.usage.get((i,u),0)+1
        self.accepted.append(dict(id=ident,release=release,deadline=deadline,slots=list(slots)))
        return True

    def certificate(self):
        for p in self.accepted:
            s=p['slots'];assert p['release']<=s[0]<s[1]<s[2]<=p['deadline']
        for (i,t),n in self.usage.items():assert n<=self.floors[i]+self.extra(i,t)
        for i,start,end in self.leases:
            assert end-start>=self.minimum_lease
            for t in range(start,end):assert self.extra(i,t)<=self.maximum
        return dict(offered=len(self.accepted)+len(self.rejected),admitted=len(self.accepted),
            rejected=len(self.rejected),extra_unit_slots=sum(e-s for i,s,e in self.leases),
            leases=self.leases,accepted=self.accepted,rejected_ids=self.rejected)


def execute_certificate(controller,actual_floor):
    """Independent execution. Missing predecessors or capacity cause failures.

    actual_floor(stage,time) is accessed only by this execution layer, never
    by the controller. Failed reservations are not silently rescheduled.
    """
    cert=controller.certificate();progress={p['id']:0 for p in cert['accepted']}
    scheduled={}
    for p in cert['accepted']:
        for i,t in enumerate(p['slots']):scheduled.setdefault((t,i),[]).append(p['id'])
    breach=[]
    for (t,i),ids in sorted(scheduled.items()):
        floor=actual_floor(i,t)
        if floor<controller.floors[i]:breach.append((i,t))
        available=floor+controller.extra(i,t)
        for ident in ids:
            if progress[ident]==i and available>0:progress[ident]+=1;available-=1
    timely=sum(v==3 for v in progress.values())
    return dict(**cert,timely=timely,late_or_failed_admitted=cert['admitted']-timely,
        timely_per_offered=timely/max(1,cert['offered']),
        rejected_per_offered=cert['rejected']/max(1,cert['offered']),floor_breach_slots=breach)
