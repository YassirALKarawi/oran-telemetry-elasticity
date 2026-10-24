"""New-seed elasticity experiment with explicit capacity cost and actuation lag."""
import argparse
import json
import statistics as st
import unittest
from pathlib import Path
from baseline.simulate import trace
from experiment import bootstrap_ci
from engine_v4 import run,CONFIGS
from elastic import solve_elastic


class Tests(unittest.TestCase):
    def reports(self,q=0):
        return [dict(q=[q,q],arrival=[1,2],service=[1,2],variance=[1,1],time=0,capacity=3)
                for _ in range(3)]

    def test_resource_bounds(self):
        extra,weights,_=solve_elastic(self.reports(200),10,[0,0,0],maximum=1)
        self.assertEqual(extra[0],0)
        self.assertTrue(all(0<=x<=1 for x in extra[1:]))
        self.assertTrue(all(abs(sum(w)-1)<1e-12 for w in weights))

    def test_no_scaling_cost_for_fixed(self):
        events=trace(17,100,'nominal')
        r=run(events,'fixed',warmup=10,measure=50)
        self.assertEqual(r['abstract_cost'],0)
        self.assertEqual(r['maximum_active_extra'],0)

    def test_always_on_charged(self):
        events=trace(17,100,'nominal')
        r=run(events,'always_on',warmup=10,measure=50)
        self.assertEqual(r['extra_service_unit_slots'],600)

    def test_activation_not_instant(self):
        events=[([4,6],[4,3,3])]*100
        r=run(events,'elastic_cap3',warmup=10,measure=50,activation_delay=10)
        self.assertIsNotNone(r['first_nonzero_extra_slot'])
        self.assertGreaterEqual(r['first_nonzero_extra_slot'],10)

    def test_same_exogenous_trace_and_report_budget(self):
        events=trace(19,100,'nominal')
        rr=[run(events,n,warmup=10,measure=50,seed=19) for n in CONFIGS]
        for k in ('trace_hash','requests','delivered','arrivals'):
            self.assertTrue(all(x[k]==rr[0][k] for x in rr))

    def test_finite_infeasible_result(self):
        r=self.reports(1000)
        _,_,d=solve_elastic(r,10,[0,0,0],maximum=0)
        self.assertFalse(d['model_feasible'])
        self.assertGreater(d['maximum_normalized_slack'],0)

    def test_reproducibility_and_cap(self):
        events=trace(21,100,'nominal')
        r=run(events,'elastic_cap1',warmup=10,measure=50)
        self.assertEqual(r,run(events,'elastic_cap1',warmup=10,measure=50))
        self.assertLessEqual(r['maximum_active_extra'],2)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--test',action='store_true')
    p.add_argument('--seeds',type=int,default=20)
    p.add_argument('--measure',type=int,default=3000)
    p.add_argument('--output',default='results_v4.json')
    a=p.parse_args()
    if a.test:
        unittest.main(argv=['evaluate_v4.py'])
        return
    if a.seeds<2 or a.measure<1:
        p.error('At least two seeds and positive measurement horizon required')
    rows,summaries,paired=[],[],[]
    for scenario,delay,loss in [('nominal',3,.05),('bursty_transport',3,.05),
                               ('bursty_compute',3,.05),('bursty_transport',9,.15)]:
        label=f'{scenario}_delay{delay}_loss{loss}'
        for seed in range(3000,3000+a.seeds):
            events=trace(seed,300+a.measure+40,scenario)
            group=[dict(case=label,**run(events,n,seed=seed,measure=a.measure,delay=delay,loss=loss)) for n in CONFIGS]
            for key in ('trace_hash','requests','delivered','arrivals'):
                assert all(r[key]==group[0][key] for r in group)
            for r in group:
                r['weighted_violation']=sum(r['violation'][s]*r['arrivals'][s] for s in range(2))/max(1,sum(r['arrivals']))
            rows.extend(group)
        for name in CONFIGS:
            selected=[r for r in rows if r['case']==label and r['config']==name]
            summaries.append(dict(case=label,config=name,
                                  violation=[st.fmean(r['violation'][s] for r in selected) for s in range(2)],
                                  weighted_violation=st.fmean(r['weighted_violation'] for r in selected),
                                  mean_extra_capacity=st.fmean(r['mean_extra_capacity'] for r in selected),
                                  cost=st.fmean(r['abstract_cost'] for r in selected),
                                  switching_units=st.fmean(r['activation_switching_units'] for r in selected),
                                  modeled_feasible_fraction=st.fmean(r['modeled_feasible_checks']/r['modeled_feasibility_checks'] for r in selected)))
        selected={r['seed']:r for r in rows if r['case']==label and r['config']=='elastic_cap3'}
        for comparator in ('fixed','always_on','elastic_cap1'):
            baseline={r['seed']:r for r in rows if r['case']==label and r['config']==comparator}
            for metric,fn in [('class0',lambda r:r['violation'][0]),('class1',lambda r:r['violation'][1]),
                              ('cost',lambda r:r['abstract_cost'])]:
                diff=[fn(selected[s])-fn(baseline[s]) for s in selected]
                paired.append(dict(case=label,comparator=comparator,metric=metric,
                                   difference=st.fmean(diff),ci95=bootstrap_ci(diff)))
        print(label+' completed',flush=True)
    data=dict(status='synthetic_capacity_elasticity_pilot',seed_start=3000,seeds=a.seeds,
              measurement_slots=a.measure,activation_delay_slots=10,slot_ms=20,
              switching_cost_per_unit=.25,unit_slot_cost=1,
              runs=rows,summaries=summaries,paired_comparisons=paired)
    Path(a.output).write_text(json.dumps(data,indent=2),encoding='utf-8')
    print(json.dumps(summaries,indent=2))


if __name__=='__main__':
    main()
