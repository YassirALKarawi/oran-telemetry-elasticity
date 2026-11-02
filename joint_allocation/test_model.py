import unittest
from model import exact,brute,verify
from experiment import instance

class Tests(unittest.TestCase):
    def test_exhaustive_reference(self):
        for seed in range(60000,60020):
            a=instance(seed,4);x=exact(a);b=brute(a)
            self.assertEqual((x['served'],x['cost']),(b['served'],b['cost']))
    def test_overload_rejected(self):
        a=instance(12,2)
        for link in a['links'].values():link['capacity']=0
        self.assertEqual(exact(a)['served'],0)
    def test_impossible_delay(self):
        a=instance(13,2)
        for r in a['requests']:r['deadline']=0
        self.assertEqual(exact(a)['served'],0)

if __name__=='__main__':unittest.main()
