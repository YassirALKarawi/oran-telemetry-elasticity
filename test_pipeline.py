import unittest
from baseline.simulate import trace
from engine_static import run
from pipeline_control import project,fluid_service
from paper_evaluation import execute


class PipelineTests(unittest.TestCase):
    def test_fluid_conservation(self):
        for q in ([0,0],[1.2,9.8],[10,3],[0,20]):
            used=fluid_service(q,[.4,.6],5)
            self.assertAlmostEqual(sum(used),min(sum(q),5))
            self.assertTrue(all(0<=used[s]<=q[s] for s in (0,1)))

    def test_projection_uses_pending_actions(self):
        reports=[dict(q=[20,20],arrival=[1,1],capacity=1,time=0) for i in range(3)]
        ledger=[([0,0,0],[[.5,.5]]*3)]
        a=project(reports,0,10,ledger,[])
        b=project(reports,0,10,ledger,[(2,[0,3,3],[[.5,.5]]*3)])
        self.assertEqual(a[0],b[0])
        self.assertLess(sum(b[1]),sum(a[1]))

    def test_future_command_excluded(self):
        r=[dict(q=[4,4],arrival=[1,1],capacity=4,time=0) for i in range(3)]
        ledger=[([0,0,0],[[.5,.5]]*3)]
        self.assertEqual(project(r,0,5,ledger,[]),project(r,0,5,ledger,[(5,[0,3,3],[[.3,.7]]*3)]))

    def test_gate_pathwise_equivalence(self):
        events=trace(803,3340,'bursty_transport')
        a=execute(events,'gated','static_2_0',803,3,.05,100)
        b=execute(events,'fixed','static_2_0',803,3,.05,100)
        self.assertEqual(a,b)

    def test_gate_short_delay_is_pipeline(self):
        events=trace(804,3340,'bursty_transport')
        a=execute(events,'gated','static_2_0',804,3,.05,10)
        b=execute(events,'pipeline','static_2_0',804,3,.05,10)
        self.assertEqual(a,b)

    def test_no_future_leakage(self):
        prefix=trace(9,100,'nominal')
        logs=[]
        for suffix in ([([0,0],[1,1,1])]*40,[([20,30],[9,9,9])]*40):
            log=[]
            run(prefix+suffix,'elastic_cap3',seed=9,warmup=20,measure=80,audit_log=log,pipeline_mode='full')
            logs.append(log)
        self.assertEqual(logs[0][:100],logs[1][:100])


if __name__=='__main__':
    unittest.main()
