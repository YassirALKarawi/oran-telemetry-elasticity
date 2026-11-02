"""Independently reconcile post-selection diagnostic pairs and bootstrap intervals."""
import json
from pathlib import Path
from reliability_study import TEST_CASES,TEST_SEEDS
from extension_evaluation import interval
from pending_diagnostic import job
p=Path(__file__).parent
d=json.loads((p/'pending_diagnostic.json').read_text());b=json.loads((p/'reliability_results.json').read_text())
assert len(d['runs'])==140 and len(d['summaries'])==7
for row in d['summaries']:
 a=sorted([x for x in d['runs'] if x['case']==row['case']],key=lambda x:x['seed'])
 full=sorted([x for x in b['runs'] if x['case']==row['case'] and x['method']=='risk'],key=lambda x:x['seed'])
 assert [x['seed'] for x in a]==TEST_SEEDS
 assert all(x['trace_hash']==y['trace_hash'] for x,y in zip(a,full))
 delta=[y['abstract_cost']-x['abstract_cost'] for x,y in zip(a,full)]
 assert interval(delta)==tuple(row['full_minus_applied_ci']) or list(interval(delta))==row['full_minus_applied_ci']
 assert abs(sum(x['abstract_cost'] for x in a)/20-row['applied_only']['cost'])<1e-8
 for x in a:assert abs(x['abstract_cost']-x['extra_service_unit_slots']-.25*x['activation_switching_units'])<1e-8
r=job((TEST_SEEDS[0],TEST_CASES[0]));old=d['runs'][0]
assert r==old
print(json.dumps({'runs':140,'matched_trace_pairs':140,'summaries':7,'fresh_replay':True,'passed':True}))
