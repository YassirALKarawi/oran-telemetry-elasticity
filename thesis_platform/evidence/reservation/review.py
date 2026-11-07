"""Independently reconstruct the allocation ledger and the deadline counts."""
import hashlib
import json
import statistics
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

archive=Path(sys.argv[1])
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    def read(name):
        return json.loads(z.read(name))
    p=read('protocol.json')
    freeze=read('selection.json')
    phases={}
    history=[]
    details={}
    for phase in ('development','evaluation'):
        lines=z.read(phase+'.jsonl').splitlines()
        rows=iter(map(json.loads,lines))
        groups=defaultdict(list)
        for t in p['phases'][phase]:
            for method in t['order']:
                counts=[[0]*4 for _ in range(2)]
                active=10
                for i,rates in enumerate(t['rates_mbps']):
                    r=next(rows)
                    assert (r['seed'],r['epoch'],r['rates'],r['active'],r['method'])==(t['seed'],i,rates,active,method)
                    assert r['sent']==[v*250 for v in rates]
                    for c,limit in enumerate(p['class_deadlines_ms']):
                        h=r['delay_ms_ceiling_histogram'][c]
                        assert r['received'][c]==sum(h.values())
                        on=sum(v for k,v in h.items() if int(k)<=limit)
                        v=[r['sent'][c],on,r['received'][c]-on,r['sent'][c]-r['received'][c]]
                        assert min(v)>=0 and sum(v[1:])==v[0]
                        counts[c]=[a+b for a,b in zip(counts[c],v)]
                    if i<4:
                        action=r['thesis']
                        if method=='proportional':
                            n=sum(r['sent'])
                            action=max(1,min(19,(40*r['sent'][0]+n)//(2*n)))
                        if method.startswith('floor') or method=='guarded':
                            f=freeze['units'] if method=='guarded' else int(method[5:])
                            action=min(action,20-f)
                        assert r['applied_next']==[action,20-action]
                        assert b'CONTROL ACK rx' in z.read(f'control-{t["seed"]}-{method}-{i}.log')
                        active=action
                        history.append(active)
                a,b=counts
                groups[method].append([100*a[1]/a[0],100*b[1]/b[0],100*(a[1]+b[1])/(a[0]+b[0])])
                details[t['seed'],method]=counts
        assert next(rows,None) is None
        means={m:list(map(statistics.mean,zip(*scores))) for m,scores in groups.items()}
        for m,s in read(phase+'-scores.json').items():
            assert all(abs(a-b)<1e-10 for a,b in zip(means[m],s['means']))
        phases[phase]=means
        if phase=='development':
            t=means['proportional'][0]+max(0,means['thesis'][0]-means['proportional'][0])/2
            eligible=[n for n in (4,6,8) if means[f'floor{n}'][0]>=t]
            best=max(eligible,key=lambda n:(means[f'floor{n}'][1],-n)) if eligible else max((4,6,8),key=lambda n:(*means[f'floor{n}'][:2],-n))
            assert best==freeze['units'] and eligible==freeze['eligible']
    assert len(history)==132 and history==list(map(int,z.read('agent-actions.txt').splitlines()))
    frames=z.read('frames.tsv').lower()
    assert frames.count(b'riccontrolrequest')==frames.count(b'riccontrolacknowledge')==132
print('Development',phases['development'])
print('Floor',freeze['units'],'eligible',eligible)
print('Evaluation',phases['evaluation'])
m=phases['evaluation']
gain=m['thesis'][0]-m['proportional'][0]
remaining=m['guarded'][0]-m['proportional'][0]
print('Original advantage, guarded advantage, retained fraction',gain,remaining,remaining/gain if gain>0 else None)
print('Mandatory test',gain>0 and remaining>=gain/2 and m['guarded'][1]>m['thesis'][1])
print('Evaluation counts by method/class [sent,timely,late,missing]')
for method in ('thesis','guarded','proportional'):
    print(method,[list(map(sum,zip(*(details[t['seed'],method][c] for t in p['phases']['evaluation'])))) for c in range(2)])
print('SHA256',hashlib.sha256(archive.read_bytes()).hexdigest())
