"""Necessary arrival-window service-capacity test, independent of policy.

All packets released in [a,b) must traverse each stage by b+Dmax if every
deadline is to be met. They cannot use service before a. If their count exceeds
the total available bottleneck service in [a,b+Dmax), zero misses are impossible.
This test gives a necessary condition only, not sufficient schedulability.
"""
import json
from pathlib import Path
from baseline.simulate import trace, DEADLINES

root = Path(__file__).resolve().parent
data = json.loads((root/'results_v3.json').read_text())
rows=[]
for scenario,stage in [('bursty_transport',1),('bursty_compute',2)]:
    for seed in range(data['seed_start'],data['seed_start']+data['seeds']):
        events = trace(seed,300+data['measurement_slots']+40,scenario)
        for a in range(180,len(events),600):
            b=a+110
            end=b+max(DEADLINES)
            if a<300 or b>300+data['measurement_slots'] or end>len(events):
                continue
            arrivals=sum(sum(events[t][0]) for t in range(a,b))
            capacity=sum(events[t][1][stage] for t in range(a,end))
            rows.append(dict(scenario=scenario,seed=seed,start=a,end=b,
                             arrivals=arrivals,available_service=capacity,
                             unavoidable_late_lower_bound=max(0,arrivals-capacity)))
out=dict(test='necessary_not_sufficient_capacity_test',windows=rows,
         violating_windows=sum(r['unavoidable_late_lower_bound']>0 for r in rows),
         tested_windows=len(rows))
(root/'feasibility_audit.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(f"Necessary condition failed in {out['violating_windows']} of {len(rows)} tested burst windows.")
