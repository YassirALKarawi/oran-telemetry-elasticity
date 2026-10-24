"""Independent checks for calibrated controllers and variable command delays."""
import math
import random
import unittest
from baseline.simulate import allocate, trace, DEADLINES
from engine_static import run
from pipeline_control import project, solve_pipeline
from reliability_study import Controller, grid, workload, schedule, upper
from independent_validation import reference_replay


class ReliabilityTests(unittest.TestCase):
    def reports(self):
        rng=random.Random(317)
        return [dict(q=[rng.randrange(20),rng.randrange(30)],arrival=[.9,2.1],
                     service=[1.,2.],variance=[1.,2.],capacity=5,time=0) for _ in range(3)]

    def test_eta_one_regression(self):
        r=self.reports(); ledger=[([0,0,0],[[.5,.5]]*3)]
        a=grid(r,0,[0,0,0],10,ledger,[])
        b=solve_pipeline(r,0,[0,0,0],10,ledger,[])
        self.assertEqual(a,b)

    def test_uncached_enumeration(self):
        r=self.reports(); ledger=[([0,0,0],[[.5,.5]]*3)]
        q=project(r,0,10,ledger,[])
        d=[[q[i][s]+5*r[i]['arrival'][s]+math.sqrt(5*r[i]['variance'][s])+1 for s in range(2)] for i in range(3)]
        for eta in (.25,.5,.75,1.):
            candidates=[]
            for x in range(4):
                for y in range(4):
                    e=[0,x,y];cost=sum(e)*1.25
                    for k in range(1,20):
                        g=[allocate([k/20,1-k/20],r[i]['capacity']+e[i]) for i in range(3)]
                        ratios=[sum(d[i][s]/max(.001,g[i][s])/DEADLINES[s]/eta for i in range(3)) for s in range(2)]
                        worst=max(ratios)
                        score=(0,cost,worst,sum(ratios),k) if worst<=1 else (1,worst,cost,sum(ratios),k)
                        candidates.append((score,e,k))
            expected=min(candidates,key=lambda z:z[0])
            actual=grid(r,0,[0,0,0],10,ledger,[],eta=eta)
            self.assertEqual(actual[0],expected[1])
            self.assertEqual(actual[1],[[expected[2]/20,1-expected[2]/20]]*3)

    def test_constant_schedule_regression(self):
        events=trace(78,140,'nominal')
        a=run(events,'elastic_cap3',seed=78,warmup=20,measure=80,controller=Controller('risk',.75))
        b=run(events,'elastic_cap3',seed=78,warmup=20,measure=80,controller=Controller('risk',.75),activation_schedule=[10]*28)
        self.assertEqual(a,b)

    def test_announced_variable_delay_and_command_order(self):
        events=[([0,0],[5,5,5])]*60
        seen=[];log=[]
        def command(r,t,previous,lag,ledger,pending):
            seen.append((t,lag))
            x=1 if t==0 else 2 if t==5 else 3
            return [0,x,0],[[.5,.5]]*3,dict(model_feasible=True,maximum_normalized_slack=0)
        run(events,'elastic_cap3',warmup=0,measure=20,controller=command,
            activation_schedule=[10,5]+[50]*10,audit_log=log)
        self.assertEqual(seen[:2],[(0,10),(5,5)])
        self.assertEqual(log[9]['capacities'],[5,5,5])
        self.assertEqual(log[10]['capacities'],[5,7,5])

    def test_future_suffix_not_visible(self):
        prefix=trace(19,100,'nominal');logs=[]
        for suffix in ([([0,0],[1,1,1])]*40,[([20,30],[9,9,9])]*40):
            log=[]
            run(prefix+suffix,'elastic_cap3',seed=19,warmup=20,measure=80,
                controller=Controller('risk',.75),activation_schedule=[1,5,10,25,50]*6,audit_log=log)
            logs.append(log)
        self.assertEqual(logs[0][:100],logs[1][:100])

    def test_workload_and_jitter_contract(self):
        for kind in ('periodic','compute','markov','compound','jitter'):
            a=workload(13001,kind)
            self.assertEqual(a,workload(13001,kind))
            self.assertEqual(len(a),3340)
            self.assertTrue(all(all(isinstance(v,int) and v>=0 for v in arr) for arr,_ in a))
            if kind=='compound': self.assertTrue(all(v%3==0 for arr,_ in a for v in arr))
        self.assertEqual(set(schedule(13001,'jitter',10)),{1,5,10,25,50})

    def test_bootstrap_bounds_and_zero_caveat(self):
        self.assertEqual(upper([0]*20),0)
        self.assertAlmostEqual(upper([.03]*20),.03)
        self.assertGreater(1-.05**(1/20),.13)

    def test_independent_replay_with_jitter(self):
        events=workload(13007,'compound')[:540]
        for method,param in [('risk',.75),('hpa',.85),('dpp',.1),('no_ledger',.75)]:
            log=[]
            actual=run(events,'elastic_cap3',seed=13007,warmup=100,measure=400,
                       controller=Controller(method,param),activation_schedule=schedule(13007,'jitter',10),audit_log=log)
            expected=reference_replay(events,log,100,400)
            for k,v in expected.items(): self.assertEqual(actual[k],v,(method,k))


if __name__=='__main__': unittest.main()
