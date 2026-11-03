import unittest
from model import Controller, Scenario, run


class MechanismTests(unittest.TestCase):
    def test_conflict_is_attempt_not_overload(self):
        a = run(Scenario('x'), 'reports_only')
        b = run(Scenario('x'), 'ack_aware')
        self.assertEqual((a['applied'], a['capacity_conflicts'], a['actual_overloads']), (1, 1, 0))
        self.assertEqual((b['applied'], b['capacity_conflicts'], b['deferred']), (1, 0, 1))

    def test_joint_alternative_uses_both_resources(self):
        b = run(Scenario('x', routes=2), 'ack_aware')
        self.assertEqual(b['applied'], 2)
        self.assertEqual(set(b['final_load'].values()), {6})

    def test_zero_delay_collapse(self):
        s = Scenario('x', execution_delay=0, acknowledgement_delay=0, report_times=(0, 1))
        a, b = run(s, 'reports_only'), run(s, 'ack_aware')
        # Compare decisions and outcomes, not different internal estimators.
        choices = lambda r: [(e['time'], e['request'], e['route']) for e in r['trace'] if e['event'] == 'arrival']
        self.assertEqual(choices(a), choices(b))
        for key in ['issued', 'deferred', 'applied', 'capacity_conflicts']:
            self.assertEqual(a[key], b[key])
        self.assertEqual(a['final_load'], b['final_load'])

    def test_fresh_report_does_not_double_count(self):
        s = Scenario('x', report_times=(0, 4), arrivals=((0, 6), (4, 4)))
        self.assertEqual(run(s, 'ack_aware')['applied'], 2)

    def test_success_ack_keeps_reservation(self):
        c = Controller('ack_aware', {'a': 10})
        c.decide(0, 6, [('a',)])
        c.acknowledge(3, 0, True)
        self.assertEqual(c.committed(), {'a': 6})

    def test_missing_ack_is_not_failure(self):
        s = Scenario('x', execution_delay=1, acknowledgement_delay=None,
                     arrivals=((0, 6), (3, 6)), fail_first=True)
        self.assertEqual(run(s, 'ack_aware')['deferred'], 1)

    def test_confirmed_failure_releases(self):
        s = Scenario('x', execution_delay=1, acknowledgement_delay=1,
                     arrivals=((0, 6), (3, 6)), fail_first=True)
        self.assertEqual(run(s, 'ack_aware')['applied'], 1)
        self.assertEqual(run(s, 'issue_ledger')['applied'], 0)

    def test_reference_equivalence(self):
        for delay in range(5):
            for routes in [1, 2]:
                s = Scenario('x', routes=routes, execution_delay=delay)
                a, b = run(s, 'ack_aware'), run(s, 'causal_reference')
                a.pop('policy'); b.pop('policy'); self.assertEqual(a, b)

    def test_no_future_reports_and_no_duplicate_commands(self):
        c = Controller('ack_aware', {'a': 10})
        with self.assertRaises(AssertionError): c.report(0, 1, {'a': 0}, {})
        c.decide(0, 6, [('a',)])
        with self.assertRaises(ValueError): c.decide(0, 1, [('a',)])
        c.report(3, 2, {'a': 6}, {0: True})
        c.report(4, 1, {'a': 0}, {})
        self.assertEqual(c.committed(), {'a': 6})


if __name__ == '__main__': unittest.main()
