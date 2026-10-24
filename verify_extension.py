"""Whole-artifact invariants and statistical implementation tests."""
import hashlib
import json
import unittest
from pathlib import Path
from extension_evaluation import sign_test, interval

ROOT=Path(__file__).resolve().parent


class StatisticalTests(unittest.TestCase):
    def test_sign_all_equal(self):
        self.assertEqual(sign_test([0]*20)['p_raw'],1.)

    def test_sign_all_better(self):
        self.assertEqual(sign_test([-1]*20)['p_raw'],2/2**20)

    def test_sign_balanced(self):
        self.assertEqual(sign_test([-1,1]*10)['p_raw'],1.)

    def test_constant_bootstrap(self):
        self.assertEqual(interval([4.]*20),[4.,4.])


def verify():
    data=json.loads((ROOT/'extension_results.json').read_text())
    assert data['protocol_sha256']==hashlib.sha256((ROOT/'EXTENSION_PROTOCOL.md').read_bytes()).hexdigest()
    assert len(data['primary_runs'])==480
    assert len(data['sensitivity_runs'])==120
    assert {r['seed'] for r in data['primary_runs']}==set(range(6000,6020))
    assert {r['seed'] for r in data['sensitivity_runs']}==set(range(7000,7010))
    for case in {r['case'] for r in data['primary_runs']}:
        for seed in range(6000,6020):
            group=[r for r in data['primary_runs'] if r['case']==case and r['seed']==seed]
            assert len(group)==6
            for key in ('trace_hash','arrivals','requests','delivered'):
                assert all(r[key]==group[0][key] for r in group)
    for r in data['primary_runs']+data['sensitivity_runs']:
        assert r['abstract_cost']==r['extra_service_unit_slots']+.25*r['activation_switching_units']
        assert r['maximum_active_extra']<=6
        for s in (0,1):
            assert r['violation'][s]==(r['late_completed'][s]+r['unfinished'][s])/r['arrivals'][s]
    ordered=sorted(data['paired'],key=lambda x:x['p_raw'])
    running=0.
    for j,item in enumerate(ordered):
        running=max(running,min(1,(12-j)*item['p_raw']))
        assert item['p_holm']==running
    print('PASS: 600 runs, locked protocol hash, seed ranges, paired budgets, cohort rates, capacity, cost and 12-test Holm adjustment.')


if __name__=='__main__':
    verify()
