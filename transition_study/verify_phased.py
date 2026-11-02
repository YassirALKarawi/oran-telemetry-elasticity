import gzip,json,hashlib
from pathlib import Path
root=Path(__file__).parent
d=json.loads(gzip.decompress((root/'phased_results.json.gz').read_bytes()))
assert d['code_sha256']==hashlib.sha256((root/'phased.py').read_bytes()).hexdigest()
assert len(d['rows'])==60
checked=0
for row in d['rows']:
    a=row['instance'];setup,ack,cutover=row['phases']
    for c in row['candidates']:
        p=c['plan']
        if p is None:continue
        cpu=[[0]*a['horizon'] for _ in range(2)];link=[[0]*a['horizon'] for _ in range(2)]
        copy=[0]*a['horizon'];temporary=[0]*a['horizon'];cost=0
        for j,k in enumerate(p['placement']):
            start=p['starts'][j];ready=p['ready'][j];copied=p['copied'][j];end=p['ends'][j]
            assert ready==start+setup and end==copied+ack+cutover
            assert copied-ready==(a['state_size'][j]+a['copy_rate'][j][k]-1)//a['copy_rate'][j][k]
            assert 0<=start<=ready<copied<=end<=a['horizon']
            for t in range(start,a['horizon']):cpu[k][t]+=a['cpu'][j]
            for t in range(start,end):temporary[t]+=a['cpu'][j]
            for t in range(ready,copied):copy[t]+=a['copy_rate'][j][k];link[k][t]+=a['copy_rate'][j][k]
            for t in range(copied,a['horizon']):link[k][t]+=a['traffic'][j]
            cost+=a['cpu'][j]*(end*a['source_price']+(a['lifetime']-start)*a['price'][k])
        assert max(copy)<=a['copy_link'] and max(temporary)<=a['temporary_cpu']
        for k in range(2):assert max(cpu[k])<=a['capacity'][k] and max(link[k])<=a['link'][k]
        assert cost==p['cost'];checked+=1
    assert (row['joint'] is None)==(row['screened'] is None)
    if row['joint']:assert row['joint']['cost']<=row['screened']['cost']
receipt=dict(status='passed',instances=60,independently_verified_schedules=checked)
(root/'phased_verification.json').write_text(json.dumps(receipt,indent=2))
print(receipt)
