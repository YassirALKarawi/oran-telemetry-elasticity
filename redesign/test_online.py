import random,unittest
from online import ReservationController,execute_certificate

class OnlineTests(unittest.TestCase):
    def test_causal_prefix(self):
        a=ReservationController();b=ReservationController()
        for ident in range(12):
            t=ident//3
            self.assertEqual(a.observe(ident,t,t+7),b.observe(ident,t,t+7))
        before=a.certificate()
        for ident in range(12,20):b.observe(ident,8,17)
        self.assertEqual(before['accepted'],b.accepted[:len(before['accepted'])])
        self.assertEqual(before['leases'],b.leases[:len(before['leases'])])

    def test_execution_and_bounds(self):
        for seed in range(50):
            rng=random.Random(seed);c=ReservationController(lag=seed%8)
            for ident,t in enumerate(sorted(rng.randrange(20) for _ in range(50))):c.observe(ident,t,t+rng.choice([4,8,12]))
            r=execute_certificate(c,lambda i,t:c.floors[i])
            self.assertEqual(r['timely'],r['admitted'])
            self.assertEqual(r['offered'],r['rejected']+r['timely'])

    def test_floor_breach_visible(self):
        c=ReservationController(maximum=0);c.observe(0,0,4)
        r=execute_certificate(c,lambda i,t:0)
        self.assertEqual(r['timely'],0);self.assertTrue(r['floor_breach_slots'])

    def test_lag_prevents_early_expansion(self):
        c=ReservationController(floors=(1,0,1),lag=8)
        self.assertFalse(c.observe(0,0,5))

if __name__=='__main__':unittest.main()
