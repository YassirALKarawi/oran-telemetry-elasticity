"""Held-out evaluation of two-class surrogate-constrained allocation."""
import argparse
import json
import statistics as st
import unittest
from pathlib import Path
from baseline.simulate import trace
from experiment import bootstrap_ci, run as run_v2
from engine_v3 import run
from constraints import solve, evaluate

NAMES = ("modern_oldest", "modern_risk", "constrained_periodic",
         "constrained_oldest", "constrained_risk", "constrained_no_margin")


class Tests(unittest.TestCase):
    def reports(self, q=0, capacity=5):
        return [dict(q=[q, q], arrival=[.9, 2.1], service=[1, 2], variance=[1, 1],
                     capacity=capacity, time=0) for _ in range(3)]

    def test_exact_grid_solution(self):
        reports = self.reports(15)
        weights, info = solve(reports, 4)
        scores = [max(evaluate(reports, 4, k/20)) for k in range(1,20)]
        self.assertAlmostEqual(max(info["predicted_ratios"]), min(scores))
        self.assertAlmostEqual(sum(weights[0]), 1)

    def test_feasibility_is_exposed(self):
        _, info = solve(self.reports(1000, 1), 10)
        self.assertFalse(info["model_feasible"])
        self.assertGreater(info["maximum_normalized_slack"], 0)

    def test_margin_nonnegative_effect(self):
        r = self.reports(5)
        without = evaluate(r, 20, .5, False)
        with_margin = evaluate(r, 20, .5, True)
        self.assertTrue(all(a >= b for a,b in zip(with_margin, without)))

    def test_both_classes_in_objective(self):
        r = self.reports()
        for x in r:
            x['q'] = [0, 300]
        _, info = solve(r, 0)
        self.assertLess(info['alpha'], .5)

    def test_v2_numeric_equivalence(self):
        events = trace(77, 120, 'nominal')
        a = run_v2(events, 'modern_risk', warmup=10, measure=60, seed=77)
        b = run(events, 'modern_risk', warmup=10, measure=60, seed=77)
        for k in a:
            self.assertEqual(a[k], b[k])

    def test_equal_trace_budget_and_reproducibility(self):
        events = trace(88, 120, 'bursty_transport')
        rs = [run(events, name, warmup=10, measure=60, seed=88) for name in NAMES]
        for key in ('trace_hash','requests','delivered','arrivals'):
            self.assertTrue(all(r[key]==rs[0][key] for r in rs))
        self.assertEqual(rs[-2], run(events, 'constrained_risk', warmup=10, measure=60, seed=88))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--test', action='store_true')
    p.add_argument('--seeds', type=int, default=20)
    p.add_argument('--measure', type=int, default=3000)
    p.add_argument('--output', default='results_v3.json')
    a = p.parse_args()
    if a.test:
        unittest.main(argv=['evaluate_v3.py'])
        return
    if a.seeds < 2 or a.measure < 1:
        p.error('At least two seeds and a positive horizon are required')
    rows, summaries, paired = [], [], []
    cases = [('nominal',3,.05), ('bursty_transport',3,.05),
             ('bursty_compute',3,.05), ('bursty_transport',9,.15)]
    for scenario, delay, loss in cases:
        label = f'{scenario}_delay{delay}_loss{loss}'
        for seed in range(2000,2000+a.seeds):
            events = trace(seed,300+a.measure+40,scenario)
            group = [dict(case=label, **run(events,name,seed=seed,measure=a.measure,
                                           delay=delay,loss=loss)) for name in NAMES]
            for key in ('trace_hash','requests','delivered','arrivals'):
                assert all(r[key]==group[0][key] for r in group)
            for r in group:
                r['weighted_violation'] = sum(r['violation'][s]*r['arrivals'][s] for s in range(2))/max(1,sum(r['arrivals']))
            rows.extend(group)
        for name in NAMES:
            rr = [r for r in rows if r['case']==label and r['config']==name]
            checks = sum(r['modeled_feasibility_checks'] for r in rr)
            summaries.append(dict(case=label,config=name,
                                  violation=[st.fmean(r['violation'][s] for r in rr) for s in range(2)],
                                  weighted_violation=st.fmean(r['weighted_violation'] for r in rr),
                                  modeled_feasible_fraction=(sum(r['modeled_feasible_checks'] for r in rr)/checks if checks else None)))
        selected = {r['seed']:r for r in rows if r['case']==label and r['config']=='constrained_risk'}
        for comparator in ('modern_oldest','modern_risk','constrained_periodic','constrained_no_margin'):
            baseline = {r['seed']:r for r in rows if r['case']==label and r['config']==comparator}
            metrics = [('class0',lambda r:r['violation'][0]),('class1',lambda r:r['violation'][1]),
                       ('weighted',lambda r:r['weighted_violation'])]
            for metric,fn in metrics:
                diff = [fn(selected[s])-fn(baseline[s]) for s in selected]
                paired.append(dict(case=label, comparator=comparator,metric=metric,
                                   difference=st.fmean(diff),ci95=bootstrap_ci(diff)))
        print(label+' completed',flush=True)
    data = dict(status='surrogate_constrained_synthetic_pilot_not_QoS_guarantee',
                seed_start=2000,seeds=a.seeds,measurement_slots=a.measure,
                runs=rows,summaries=summaries,paired_comparisons=paired)
    Path(a.output).write_text(json.dumps(data,indent=2),encoding='utf-8')
    print(json.dumps(summaries,indent=2))


if __name__=='__main__':
    main()
