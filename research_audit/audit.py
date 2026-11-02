"""Exploratory falsification, with original experiments left unchanged."""
import hashlib
import heapq
import json
import random
import statistics
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import engine_static
from baseline.simulate import DEADLINES
from reliability_study import Controller, TEST_CASES, workload, schedule

ORIGINAL_SCHEDULE = engine_static.schedule
POLICIES = [(m, s) for m in ('risk', 'static', 'maximum') for s in ('weighted', 'edf')]


def edf(queues, weights, capacity, work_conserving):
    """Global EDF across local class FIFOs, using no future information."""
    taken = [0, 0]
    for _ in range(min(capacity, sum(map(len, queues)))):
        available = [s for s in range(2) if taken[s] < len(queues[s])]
        s = min(available, key=lambda s: (queues[s][taken[s]][1] + DEADLINES[s], s))
        taken[s] += 1
    return taken


def maximum_matches(jobs, capacities):
    """jobs=(release,inclusive_deadline), independent unit-capacity matching."""
    releases = {}
    for ident, (release, deadline) in enumerate(jobs):
        releases.setdefault(release, []).append((deadline, ident))
    heap = []
    matched = 0
    for t, capacity in enumerate(capacities):
        for item in releases.get(t, []):
            heapq.heappush(heap, item)
        while heap and heap[0][0] < t:
            heapq.heappop(heap)
        for _ in range(min(capacity, len(heap))):
            heapq.heappop(heap)
            matched += 1
    return matched


def verify_matching():
    import numpy as np
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import maximum_bipartite_matching
    rng = random.Random(69240)
    for _ in range(300):
        cap = [rng.randrange(4) for _ in range(12)]
        slots = [t for t, c in enumerate(cap) for _ in range(c)]
        jobs = []
        for _ in range(rng.randrange(1, 30)):
            r = rng.randrange(12)
            jobs.append((r, r + rng.randrange(6)))
        matrix = csr_matrix(np.array([[int(r <= t <= d) for t in slots] for r, d in jobs], dtype=np.int8))
        exact = int(np.sum(maximum_bipartite_matching(matrix, perm_type='column') >= 0)) if slots else 0
        assert maximum_matches(jobs, cap) == exact
    return 300


def radio_bound(events):
    jobs = [(t, t + DEADLINES[s] - 3) for t, (a, _) in enumerate(events)
            if 300 <= t < 3300 for s in range(2) for _ in range(a[s])]
    unmatched = len(jobs) - maximum_matches(jobs, [c[0] for _, c in events])
    return {'offered': len(jobs), 'unavoidable_misses_lower_bound': unmatched,
            'unavoidable_fraction_lower_bound': unmatched / max(1, len(jobs))}


def job(task):
    seed, case = task
    kind, report_delay, loss, lag = case
    events = workload(seed, kind)
    common = dict(seed=seed, delay=report_delay, loss=loss, activation_delay=lag,
                  activation_schedule=schedule(seed, kind, lag))
    rows = []
    for method, scheduler in POLICIES:
        engine_static.schedule = edf if scheduler == 'edf' else ORIGINAL_SCHEDULE
        if method == 'risk':
            result = engine_static.run(events, 'elastic_cap3', controller=Controller('risk', .75), **common)
        else:
            config = 'always_on' if method == 'maximum' else ('static_0_2' if kind == 'compute' else 'static_2_0')
            result = engine_static.run(events, config, **common)
        rows.append(dict(method=method, scheduler=scheduler, case=list(case), **result))
    engine_static.schedule = ORIGINAL_SCHEDULE
    assert len({r['trace_hash'] for r in rows}) == 1
    assert len({tuple(r['arrivals']) for r in rows}) == 1
    bound = radio_bound(events)
    for r in rows:
        actual = sum(r['late_completed']) + sum(r['unfinished'])
        assert actual >= bound['unavoidable_misses_lower_bound'], (actual, bound)
    return {'seed': seed, 'case': list(case), 'bound': bound, 'runs': rows}


def main():
    verified = verify_matching()
    tasks = [(seed, case) for case in TEST_CASES for seed in range(24000, 24020)]
    rows = []
    with ProcessPoolExecutor(max_workers=4) as pool:
        for i, result in enumerate(pool.map(job, tasks)):
            rows.append(result)
            if (i + 1) % 10 == 0:
                print('completed', i + 1, '/', len(tasks), flush=True)
    summaries = []
    for case in TEST_CASES:
        group = [g for g in rows if g['case'] == list(case)]
        methods = []
        for method, scheduler in POLICIES:
            rr = [r for g in group for r in g['runs'] if r['method'] == method and r['scheduler'] == scheduler]
            methods.append(dict(method=method, scheduler=scheduler,
                mean_cost=statistics.fmean(r['abstract_cost'] for r in rr),
                mean_miss=[statistics.fmean(r['violation'][s] for r in rr) for s in range(2)],
                mean_total_miss=statistics.fmean((sum(r['late_completed']) + sum(r['unfinished'])) / sum(r['arrivals']) for r in rr)))
        summaries.append(dict(case=list(case), policies=methods,
            mean_radio_lower_bound=statistics.fmean(g['bound']['unavoidable_fraction_lower_bound'] for g in group),
            traces_with_positive_bound=sum(g['bound']['unavoidable_misses_lower_bound'] > 0 for g in group)))
    output = dict(status='exploratory scientific audit, not a submission-ready new contribution',
        protocol_sha256=hashlib.sha256((Path(__file__).parent / 'PROTOCOL.md').read_bytes()).hexdigest(),
        code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        independent_matching_checks=verified, runs=rows, summaries=summaries)
    (Path(__file__).parent / 'results.json').write_text(json.dumps(output, indent=2))
    print(json.dumps(summaries, indent=2))


if __name__ == '__main__':
    main()
