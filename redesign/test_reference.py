import itertools
import random
import unittest
from reference import solve


def brute(packets,cap):
    """Independent exhaustive assignment including packet rejection."""
    stages=len(cap);h=len(cap[0]);best=0
    alternatives=[]
    for r,d in packets:
        alternatives.append([None]+list(itertools.combinations(range(r,d+1),stages)))
    for assignment in itertools.product(*alternatives):
        use=[[0]*h for _ in cap];count=0
        for slots in assignment:
            if slots is None:continue
            count+=1
            for i,t in enumerate(slots):use[i][t]+=1
        if all(use[i][t]<=cap[i][t] for i in range(stages) for t in range(h)):
            best=max(best,count)
    return best


class ReferenceTests(unittest.TestCase):
    def test_independent_exhaustive(self):
        rng=random.Random(9251)
        for _ in range(60):
            cap=[[rng.randrange(3) for _ in range(5)] for i in range(3)]
            packets=[(rng.randrange(2),rng.randrange(3,5)) for _ in range(3)]
            self.assertEqual(solve(packets,cap)['admitted'],brute(packets,cap))

    def test_late_capacity_cannot_save_deadline(self):
        cap=[[1]*6,[0]*6,[1]*6]
        self.assertEqual(solve([(0,2)],cap,lag=3,max_extra=1)['admitted'],0)
        self.assertEqual(solve([(0,2)],cap,lag=1,max_extra=1)['admitted'],1)

    def test_mandatory_infeasible(self):
        self.assertFalse(solve([(0,1)],[[1]*3]*3,mandatory=[0])['feasible'])

    def test_resource_minimization(self):
        r=solve([(0,2)],[[1]*4]*3,lag=1,max_extra=3)
        self.assertEqual(r['expansion'],[0,0,0])

if __name__=='__main__':unittest.main()
