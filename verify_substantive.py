"""Independent numerical checks for the additional analytical diagnostics."""
import hashlib
import json
import math
import re
import statistics as st
from pathlib import Path
import numpy as np
from baseline.simulate import allocate
from yasq_quality import algorithms

root=Path(__file__).resolve().parent
raw=(root/'reliability_results.json').read_bytes()
data=json.loads(raw)
receipt=json.loads((root/'paper_reliability/substantive_receipt.json').read_text())
assert receipt['source_sha256']==hashlib.sha256(raw).hexdigest()
tex=(root/'paper_reliability/Manuscript.tex').read_text()
normalized=tex.replace(r'\hrule\smallskip % journal top rule'+'\n','')
normalized=normalized.replace('[x=1cm,y=1.75cm]','[x=1cm,y=1cm]')
normalized=normalized.replace(r'\noindent\begin{tikzpicture}',r'\begin{tikzpicture}')
assert receipt['algorithm_sha256']==[hashlib.sha256(a.encode()).hexdigest() for a in algorithms(normalized)]
assert receipt['algorithm_sha256']==[
    '6f70b10d38dfc63d0fb34553f6f44ef58959aad9df028f17039c87326248b304',
    '8917447f3b30c99396e0141fd77f3e320f2572a0e5d700f7e10a1e95f8e33505']
cases=list(dict.fromkeys(r['case'] for r in data['summaries']))
for c,label in zip(cases,'PMBCRLJ'):
    for m in ['risk','no_ledger','uncalibrated']:
        rr=[r for r in data['runs'] if r['case']==c and r['method']==m]
        for r in rr:
            assert r['abstract_cost']==r['extra_service_unit_slots']+.25*r['activation_switching_units']
        got=next(r for r in receipt['diagnostics'] if r['setting']==label and r['method']==m)
        assert abs(got['capacity_cost']-st.fmean(r['extra_service_unit_slots'] for r in rr))<1e-9
        assert abs(got['switching_cost']-.25*st.fmean(r['activation_switching_units'] for r in rr))<1e-9
        assert abs(got['feasible_percent']-100*st.fmean(r['modeled_feasible_checks']/r['modeled_feasibility_checks'] for r in rr))<1e-9
for c in range(3,10):
    for k in range(1,20):
        w=[k/20,1-k/20]
        r=[c*a/sum(w) for a in w]
        f=[a-math.floor(a) for a in r]
        rem=c-sum(math.floor(a) for a in r)
        g0=math.floor(r[0])+rem*int(f[0]>=f[1])
        assert allocate(w,c)==[g0,c-g0]
rng=np.random.default_rng(231026)
for _ in range(10000):
    q,a,v=rng.uniform(0,100,(3,3))
    qp,ap,vp=rng.uniform(0,100,(3,3))
    g=np.maximum(.001,rng.integers(0,10,3))
    eta=float(rng.choice([.25,.5,.75,1.]));deadline=float(rng.choice([15,40]))
    d=q+5*a+np.sqrt(5*v)+1;dp=qp+5*ap+np.sqrt(5*vp)+1
    bound=np.sum((np.abs(qp-q)+5*np.abs(ap-a)+np.sqrt(5*np.abs(vp-v)))/g)/(eta*deadline)
    difference=abs(np.sum((dp-d)/g)/(eta*deadline))
    assert difference<=bound+1e-8
    gp=np.maximum(.001,rng.integers(0,10,3))
    actual=np.sum(d/gp-d/g)/(eta*deadline)
    derived=-np.sum(d*(gp-g)/(g*gp))/(eta*deadline)
    assert np.isclose(actual,derived)
assert [l for l,g in zip('PMBCRLJ',receipt['screen_matrix']) if g[-1]]==['P','R','J']
print(json.dumps({'records_reconciled':420,'allocation_grid_checks':133,
                  'analytical_random_checks':10000,'algorithm_blocks_unchanged':True,'passed':True}))
