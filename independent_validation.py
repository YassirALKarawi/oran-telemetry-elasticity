"""Independent packet replay and uncached optimizer reference.

This is software verification of the abstraction, NOT physical validation.
The packet replay consumes logged applied actions, not controller internals.
"""
import math
import random
import statistics
import unittest
from baseline.simulate import trace
from engine_static import run
from elastic import solve_elastic

D = (15, 40)


def quotas(weights, capacity):
    ideal = [capacity * v / sum(weights) for v in weights]
    ans = [math.floor(v) for v in ideal]
    for s in sorted(range(2), key=lambda s: (-(ideal[s]-ans[s]), s))[:capacity-sum(ans)]:
        ans[s] += 1
    return ans


def reference_replay(events, log, warmup, measure):
    # Only birth times are needed for FIFO queues and deadline accounting.
    q = [[[], []] for _ in range(3)]
    admitted, late, delays = [0, 0], [0, 0], [[], []]
    backlog = 0
    for t, ((arrivals, _), action) in enumerate(zip(events, log)):
        assert action['time'] == t
        for s in range(2):
            q[0][s].extend([t] * arrivals[s])
            if warmup <= t < warmup + measure:
                admitted[s] += arrivals[s]
        # Simultaneous outgoing lists stop any same-slot multi-hop service.
        outgoing = [[[], []] for _ in range(3)]
        for i in range(3):
            cap = action['capacities'][i]
            reserve = quotas(action['weights'][i], cap)
            n = [min(reserve[s], len(q[i][s])) for s in range(2)]
            while sum(n) < cap:
                eligible = [s for s in range(2) if n[s] < len(q[i][s])]
                if not eligible:
                    break
                s = min(eligible, key=lambda s: (q[i][s][n[s]] + D[s], s))
                n[s] += 1
            for s in range(2):
                outgoing[i][s] = q[i][s][:n[s]]
                q[i][s] = q[i][s][n[s]:]
        for i in range(3):
            for s in range(2):
                if i < 2:
                    q[i+1][s].extend(outgoing[i][s])
                else:
                    for birth in outgoing[i][s]:
                        if warmup <= birth < warmup + measure:
                            delays[s].append(t-birth+1)
                            late[s] += t-birth+1 > D[s]
        if warmup <= t < warmup + measure:
            backlog += sum(len(x) for pair in q for x in pair)
    unfinished = [sum(warmup <= birth < warmup+measure for pair in q for birth in pair[s]) for s in range(2)]
    return dict(arrivals=admitted, late_completed=late, unfinished=unfinished,
                violation=[(late[s]+unfinished[s])/max(1,admitted[s]) for s in range(2)],
                mean_backlog=backlog/measure,
                completed_delay_p99=[sorted(v)[math.ceil(.99*len(v))-1] if v else None for v in delays])


def uncached_solver(reports, t, previous, maximum, delay):
    candidates = []
    for x in range(maximum+1):
        for y in range(maximum+1):
            extra = [0,x,y]
            cost = sum(extra)+.25*sum(abs(a-b) for a,b in zip(extra,previous))
            for k in range(1,20):
                ratios = [0.,0.]
                for i,r in enumerate(reports):
                    age = t+delay-r['time']
                    quota = quotas([k/20,1-k/20],int(r['capacity'])+extra[i])
                    for s in range(2):
                        qhat = max(0,r['q'][s]+age*(r['arrival'][s]-r['service'][s]))
                        demand = qhat+5*r['arrival'][s]+math.sqrt(age*r['variance'][s])+1
                        ratios[s] += demand/max(.001,quota[s])/D[s]
                worst = max(ratios)
                score = ((0,cost,worst,sum(ratios),k) if worst <= 1 else
                         (1,worst,cost,sum(ratios),k))
                candidates.append((score,extra,k,ratios))
    return min(candidates,key=lambda c:c[0])


class IndependentTests(unittest.TestCase):
    def test_reference_packet_replay(self):
        for seed in range(6):
            events=trace(seed,540,'bursty_transport')
            for name in ('static_0_0','static_2_0','elastic_cap3'):
                log=[]
                actual=run(events,name,seed=seed,warmup=100,measure=400,audit_log=log)
                expected=reference_replay(events,log,100,400)
                self.assertEqual(len(log),len(events))
                for key,value in expected.items():
                    self.assertEqual(actual[key],value,(seed,name,key))

    def test_solver_against_independent_enumeration(self):
        rng=random.Random(804)
        for _ in range(30):
            reports=[dict(q=[rng.randrange(15) for s in D],
                          arrival=[rng.random()*3 for s in D],
                          service=[rng.random()*3 for s in D],
                          variance=[rng.random()*2 for s in D],
                          capacity=rng.randrange(1,7),time=rng.randrange(21)) for i in range(3)]
            previous=[0,rng.randrange(4),rng.randrange(4)]
            extra,weights,diagnostic=solve_elastic(reports,20,previous)
            _,ref_extra,k,ratios=uncached_solver(reports,20,previous,3,10)
            self.assertEqual(extra,ref_extra)
            self.assertEqual(weights,[[k/20,1-k/20]]*3)
            for actual,expected in zip(diagnostic['predicted_ratios'],ratios):
                self.assertAlmostEqual(actual,expected,places=12)

    def test_no_arrivals(self):
        result=run([([0,0],[5,5,5])]*100,'static_0_0',warmup=10,measure=50)
        self.assertEqual(result['arrivals'],[0,0])
        self.assertEqual(result['violation'],[0,0])
        self.assertEqual(result['completed_delay_p99'],[None,None])

    def test_minimum_delay(self):
        events=[([1,0],[5,5,5])]+[([0,0],[5,5,5])]*49
        result=run(events,'static_0_0',warmup=0,measure=10)
        self.assertEqual(result['completed_delay_p99'][0],3)

    def test_zero_capacity(self):
        result=run([([1,2],[0,0,0])]*100,'static_0_0',warmup=10,measure=50)
        self.assertEqual(result['violation'],[1,1])

    def test_deadline_boundary(self):
        for completion,expected in ((14,0),(15,1)):
            events=[([1,0],[1,1,0])]+[([0,0],[1,1,0])]*49
            events[completion]=([0,0],[1,1,1])
            result=run(events,'static_0_0',warmup=0,measure=10)
            self.assertEqual(result['violation'][0],expected)

    def test_ablation_report_budgets(self):
        events=trace(12,140,'bursty_compute')
        rows=[run(events,'elastic_cap3',warmup=20,measure=80,telemetry_policy=p)
              for p in ('periodic','oldest','risk')]
        for key in ('trace_hash','arrivals','requests','delivered'):
            self.assertEqual(len({str(r[key]) for r in rows}),1)

    def test_bad_delays_rejected(self):
        events=trace(1,100,'nominal')
        for kwargs in (dict(delay=0),dict(activation_delay=0),dict(loss=1.1)):
            with self.assertRaises(ValueError):
                run(events,'elastic_cap3',warmup=10,measure=50,**kwargs)

    def test_no_future_trace_access(self):
        prefix=trace(9,100,'nominal')
        logs=[]
        for suffix in ([([0,0],[1,1,1])]*40,[([20,30],[9,9,9])]*40):
            log=[]
            run(prefix+suffix,'elastic_cap3',seed=9,warmup=20,measure=80,audit_log=log)
            logs.append(log)
        self.assertEqual(logs[0][:100],logs[1][:100])


if __name__=='__main__':
    unittest.main()
