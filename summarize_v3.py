"""Summarize actual V3 output; no selected-seed or favorable-case filtering."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent
data = json.loads((root/'results_v3.json').read_text())
lines = ['V3 SURROGATE-CONSTRAINED ALLOCATION: EXPLORATORY RESULTS', '',
         f"Runs: {len(data['runs'])}; seeds per case/config: {data['seeds']}",
         'Measured violations are percentages; paired differences are percentage points.',
         'No actual QoS guarantee follows from modeled feasibility.', '']
for x in data['summaries']:
    f = x['modeled_feasible_fraction']
    fs = 'not evaluated' if f is None else f'{100*f:.2f}%'
    lines.append(f"{x['case']:40} {x['config']:24} "
                 f"class0={100*x['violation'][0]:6.2f}% class1={100*x['violation'][1]:6.2f}% "
                 f"weighted={100*x['weighted_violation']:6.2f}% modeled_feasible={fs}")
lines += ['', 'Paired constrained_risk minus comparator: negative favors constrained_risk.',
          'Exploratory paired-bootstrap 95% intervals, without multiplicity correction.']
for x in data['paired_comparisons']:
    l,h = x['ci95']
    lines.append(f"{x['case']:40} vs {x['comparator']:24} {x['metric']:8} "
                 f"{100*x['difference']:+7.3f} CI=[{100*l:+7.3f},{100*h:+7.3f}]")
lines += ['', 'Classwise tradeoff audit against modern_oldest:']
for case in sorted({r['case'] for r in data['summaries']}):
    new = next(r for r in data['summaries'] if r['case']==case and r['config']=='constrained_risk')
    old = next(r for r in data['summaries'] if r['case']==case and r['config']=='modern_oldest')
    d = [100*(new['violation'][s]-old['violation'][s]) for s in range(2)]
    label = ('neither class has a higher sample mean' if max(d)<=0 else
             'at least one class has a higher sample mean: joint protection not established')
    lines.append(f'{case}: class0 {d[0]:+.3f} pp; class1 {d[1]:+.3f} pp; {label}')
text='\n'.join(lines)+'\n'
(root/'RESULTS_V3.txt').write_text(text,encoding='utf-8')
print(text)
