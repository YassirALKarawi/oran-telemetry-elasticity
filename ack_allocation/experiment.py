"""Run six deterministic scenarios; no statistical/generalization claims."""
import json
from pathlib import Path
from dataclasses import asdict
from model import Scenario, run

SCENARIOS = [
    Scenario('single_route_conflict'),
    Scenario('alternative_route', routes=2),
    Scenario('zero_delay', execution_delay=0, acknowledgement_delay=0, report_times=(0, 1)),
    Scenario('fresh_report_before_ack', report_times=(0, 4), arrivals=((0, 6), (4, 4))),
    Scenario('confirmed_failure', execution_delay=1, acknowledgement_delay=1,
             arrivals=((0, 6), (3, 6)), fail_first=True),
    Scenario('missing_failure_ack', execution_delay=1, acknowledgement_delay=None,
             arrivals=((0, 6), (3, 6)), fail_first=True),
]
POLICIES = ['reports_only', 'issue_ledger', 'ack_aware', 'causal_reference']

if __name__ == '__main__':
    results = [run(s, p) for s in SCENARIOS for p in POLICIES]
    for s in SCENARIOS:
        a, b = (run(s, p) for p in ['ack_aware', 'causal_reference'])
        a.pop('policy'); b.pop('policy'); assert a == b
    payload = dict(status='deterministic mechanism demonstration; novelty not established',
                   scenarios=[asdict(s) for s in SCENARIOS], results=results,
                   causal_reference_equal_in_all_scenarios=True)
    Path(__file__).with_name('results.json').write_text(json.dumps(payload, indent=2)+'\n')
    for r in results:
        print(r['scenario'], r['policy'], 'applied', r['applied'],
              'conflicts', r['capacity_conflicts'], 'deferred', r['deferred'])
