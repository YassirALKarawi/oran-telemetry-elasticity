import unittest
from contract import Ledger


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.l = Ledger()
        for c in ('transport', 'compute'):
            self.l.issue('x', c, 6, 1)

    def test_partial_failure_keeps_other_reservation(self):
        self.l.evidence('x', 'transport', 1, 0, 'applied')
        self.l.evidence('x', 'compute', 1, 0, 'not_applied')
        self.assertEqual(self.l.reserved('transport'), 6)
        self.assertEqual(self.l.reserved('compute'), 0)
        self.assertFalse(self.l.configuration_complete('x'))

    def test_timeout_retains_reservation(self):
        self.l.timeout('x', 'transport')
        self.assertEqual(self.l.reserved('transport'), 6)

    def test_compensation_issue_is_not_completion(self):
        self.l.evidence('x', 'transport', 1, 0, 'applied')
        self.l.compensate('x', 'transport')
        self.assertEqual(self.l.reserved('transport'), 6)
        self.l.evidence('x', 'transport', 1, 1, 'removed')
        self.assertEqual(self.l.reserved('transport'), 0)

    def test_failed_compensation_keeps_reservation(self):
        self.l.compensate('x', 'transport')
        self.l.evidence('x', 'transport', 1, 0, 'remove_failed')
        self.assertEqual(self.l.reserved('transport'), 6)

    def test_stale_and_duplicate_evidence(self):
        self.l.evidence('x', 'transport', 1, 3, 'applied')
        for v in (1, 3):
            self.assertFalse(self.l.evidence('x', 'transport', 1, v, 'not_applied'))
        self.assertEqual(self.l.reserved('transport'), 6)

    def test_foreign_epoch(self):
        self.assertFalse(self.l.evidence('x', 'transport', 2, 100, 'not_applied'))
        self.assertEqual(self.l.reserved('transport'), 6)

    def test_duplicate_issue(self):
        with self.assertRaises(ValueError):
            self.l.issue('x', 'transport', 6, 1)

    def test_both_components_required(self):
        self.l.evidence('x', 'transport', 1, 0, 'applied')
        self.assertFalse(self.l.configuration_complete('x'))
        self.l.evidence('x', 'compute', 1, 0, 'applied')
        self.assertTrue(self.l.configuration_complete('x'))
        self.assertEqual(self.l.reserved('transport'), 6)


if __name__ == '__main__':
    unittest.main()
