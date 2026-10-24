"""Development data, explicitly not held-out publication evidence."""
import json
import statistics
from pathlib import Path
from baseline.simulate import trace
from engine_static import run

rows=[]
for lag in (10,100):
    for seed in range(8000,8005):
        events=trace(seed,3340,'bursty_transport')
        for mode in (None,'ledger_only','margin_only','full'):
            r=run(events,'elastic_cap3',seed=seed,activation_delay=lag,pipeline_mode=mode)
            rows.append(dict(lag=lag,mode=mode,**r))
    for mode in (None,'ledger_only','margin_only','full'):
        group=[r for r in rows if r['lag']==lag and r['mode']==mode]
        print(lag,mode,[statistics.fmean(r['violation'][s] for r in group) for s in range(2)],
              statistics.fmean(r['abstract_cost'] for r in group),flush=True)
Path('pipeline_development.json').write_text(json.dumps(rows,indent=2))
