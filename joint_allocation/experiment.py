import json,random,time,hashlib,gzip
from pathlib import Path
from model import exact,greedy

def instance(seed,n=12):
    r=random.Random(seed)
    return dict(seed=seed,routes=[[0,1],[0,2],[0,1,2],[0,1,3],[0,2,3]],
        links={k:dict(capacity=r.randrange(6,15),delay=r.randrange(1,4),price=r.randrange(1,4)) for k in ['0-1','0-2','1-2','1-3','2-3']},
        servers={str(k):dict(capacity=r.randrange(6,15),processing_delay=r.randrange(1,4),price=k) for k in [1,2,3]},
        requests=[dict(bandwidth=r.randrange(1,5),cpu=r.randrange(1,5),deadline=r.randrange(4,11)) for _ in range(n)])

if __name__=='__main__':
    root=Path(__file__).parent;rows=[]
    for seed in range(61000,61100):
        a=instance(seed);results={}
        for method in ['exact','joint_greedy','placement_first']:
            start=time.perf_counter();result=exact(a) if method=='exact' else greedy(a,method)
            results[method]=dict(**result,runtime_seconds=time.perf_counter()-start)
        assert all(r['served']<=results['exact']['served'] for r in results.values())
        rows.append(dict(instance=a,results=results))
    summary={}
    for method in ['exact','joint_greedy','placement_first']:
        rr=[row['results'][method] for row in rows];matched=[row for row in rows if row['results'][method]['served']==row['results']['exact']['served']]
        summary[method]=dict(runs=100,mean_served=sum(r['served'] for r in rr)/100,mean_cost=sum(r['cost'] for r in rr)/100,
            count_matching_optimal_admission=len(matched),mean_runtime_ms=1000*sum(r['runtime_seconds'] for r in rr)/100,
            mean_cost_gap_at_matching_admission=sum(row['results'][method]['cost']-row['results']['exact']['cost'] for row in matched)/len(matched) if matched else None)
    out=dict(scope='Synthetic development benchmark. Generic algorithms, not a validated new O-RAN contribution.',
        protocol_sha256=hashlib.sha256((root/'PROTOCOL.md').read_bytes()).hexdigest(),
        model_sha256=hashlib.sha256((root/'model.py').read_bytes()).hexdigest(),rows=rows,summary=summary)
    (root/'results.json.gz').write_bytes(gzip.compress(json.dumps(out,indent=2).encode(),mtime=0))
    print(json.dumps(summary,indent=2))
