"""Independent consistency checks and fresh replays for the scientific audit."""
import gzip
import hashlib
import json
import random
from collections import deque
from pathlib import Path
from audit import ROOT, DEADLINES, POLICIES, TEST_CASES, edf, job, verify_matching

HERE = Path(__file__).resolve().parent
path = HERE / 'results.json'
data = json.loads(path.read_text() if path.exists() else gzip.decompress((HERE / 'results.json.gz').read_bytes()))
assert data['protocol_sha256'] == hashlib.sha256((HERE / 'PROTOCOL.md').read_bytes()).hexdigest()
assert data['code_sha256'] == hashlib.sha256((HERE / 'audit.py').read_bytes()).hexdigest()
assert len(data['runs']) == 140
assert len({(g['seed'], tuple(g['case'])) for g in data['runs']}) == 140
assert {g['seed'] for g in data['runs']} == set(range(24000, 24020))
assert {tuple(g['case']) for g in data['runs']} == set(TEST_CASES)
for g in data['runs']:
    assert len(g['runs']) == 6
    assert {(r['method'], r['scheduler']) for r in g['runs']} == set(POLICIES)
    for r in g['runs']:
        assert r['abstract_cost'] == r['extra_service_unit_slots'] + .25 * r['activation_switching_units']
        assert sum(r['arrivals']) == g['bound']['offered']
        assert sum(r['late_completed']) + sum(r['unfinished']) >= g['bound']['unavoidable_misses_lower_bound']
        for s in range(2):
            assert r['violation'][s] == (r['late_completed'][s] + r['unfinished'][s]) / r['arrivals'][s]
rng = random.Random(9227)
for _ in range(300):
    qq = [deque((None, b) for b in sorted(rng.randrange(60) for _ in range(rng.randrange(20)))) for s in range(2)]
    cap = rng.randrange(20)
    expected = [0, 0]
    all_packets = sorted((b + DEADLINES[s], s, i) for s in range(2) for i, (_, b) in enumerate(qq[s]))
    for _, s, _ in all_packets[:cap]:
        expected[s] += 1
    assert edf(qq, [1, 1], cap, True) == expected
assert verify_matching() == 300
for case in (TEST_CASES[2], TEST_CASES[5]):
    expected = next(g for g in data['runs'] if g['seed'] == 24000 and g['case'] == list(case))
    assert job((24000, case)) == expected
receipt = dict(status='passed', distinct_traces=140, executions=840,
    independent_matching_checks=300, independent_edf_checks=300, freshly_replayed_executions=12,
    result_sha256=hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else hashlib.sha256(gzip.decompress((HERE/'results.json.gz').read_bytes())).hexdigest())
(HERE / 'verification.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
