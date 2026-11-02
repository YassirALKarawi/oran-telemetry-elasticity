"""Post-selection matched diagnostic. No retuning or alteration of frozen results."""
import json,time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from reliability_study import workload,schedule,grid,TEST_CASES,TEST_SEEDS,summarize
from engine_static import run
from extension_evaluation import interval
class AppliedOnly:
 def __call__(self,reports,t,previous,lag,ledger,pending):
  return grid(reports,t,previous,lag,ledger,[],eta=.75)
def job(pair):
 seed,case=pair;kind,r,p,lag=case
 x=run(workload(seed,kind),'elastic_cap3',seed=seed,delay=r,loss=p,activation_delay=lag,controller=AppliedOnly(),activation_schedule=schedule(seed,kind,lag))
 return dict(case=f'{kind}_r{r}_p{p}_a{lag}',method='applied_only',**x)
def main():
 started=time.time();out=[]
 with ProcessPoolExecutor(max_workers=4) as pool:
  for x in pool.map(job,[(s,c) for c in TEST_CASES for s in TEST_SEEDS]):
   out.append(x)
   if len(out)%20==0:print('completed',len(out),flush=True)
 base=json.loads(Path('reliability_results.json').read_text())['runs'];summary=[]
 for c in dict.fromkeys(x['case'] for x in out):
  a=[x for x in out if x['case']==c];b=[x for x in base if x['case']==c and x['method']=='risk'];assert [x['seed'] for x in a]==[x['seed'] for x in b]
  d=[y['abstract_cost']-x['abstract_cost'] for x,y in zip(a,b)]
  summary.append(dict(case=c,applied_only=summarize(a),full=summarize(b),full_minus_applied_ci=interval(d)))
 Path('pending_diagnostic.json').write_text(json.dumps(dict(description='Post-selection diagnostic with unchanged eta=.75 and original held-out seeds',runs=out,summaries=summary,seconds=time.time()-started),indent=2))
 print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
