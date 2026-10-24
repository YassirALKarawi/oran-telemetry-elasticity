"""Summarize every V4 setting; expose class and cost tradeoffs."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent
d=json.loads((root/'results_v4.json').read_text())
lines=['V4: BOUNDED CAPACITY ELASTICITY PILOT','',f"Runs: {len(d['runs'])}",
       'Violations in percent. Cost in synthetic units, not currency.',
       'No calibrated delay bound or true QoS guarantee.','']
for x in d['summaries']:
    lines.append(f"{x['case']:40} {x['config']:14} "
                 f"class0={100*x['violation'][0]:6.2f}% class1={100*x['violation'][1]:6.2f}% "
                 f"weighted={100*x['weighted_violation']:6.2f}% "
                 f"extra={x['mean_extra_capacity']:.3f} cost={x['cost']:.2f}")
lines+=['','elastic_cap3 minus comparator: violations in percentage points, cost in cost units.',
        'Exploratory paired-bootstrap 95% intervals; no multiplicity correction.']
for x in d['paired_comparisons']:
    scale=1 if x['metric']=='cost' else 100
    l,h=x['ci95']
    lines.append(f"{x['case']:40} vs {x['comparator']:14} {x['metric']:7} "
                 f"delta={scale*x['difference']:+.3f} CI=[{scale*l:+.3f},{scale*h:+.3f}]")
lines+=['','No-harm sample-mean audit versus fixed:']
for case in sorted({x['case'] for x in d['summaries']}):
    fixed=next(x for x in d['summaries'] if x['case']==case and x['config']=='fixed')
    dynamic=next(x for x in d['summaries'] if x['case']==case and x['config']=='elastic_cap3')
    always=next(x for x in d['summaries'] if x['case']==case and x['config']=='always_on')
    change=[100*(dynamic['violation'][s]-fixed['violation'][s]) for s in range(2)]
    saved=100*(1-dynamic['cost']/always['cost'])
    lines.append(f'{case}: changes {change}; cost saving vs always-on {saved:.2f}%; '
                 +'both sample means non-increasing='+str(max(change)<=0))
text='\n'.join(lines)+'\n'
(root/'RESULTS_V4.txt').write_text(text,encoding='utf-8')
print(text)
