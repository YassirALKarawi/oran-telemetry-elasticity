"""Exact finite-world allocation gate; abstract units, no RL or novelty claim."""
import hashlib
import itertools
import json
from pathlib import Path
import random


def reference(capacity, worlds, requests):
    """Independent Cartesian enumeration with direct per-world constraints."""
    best, score = None, -1
    for choices in itertools.product(*[range(-1, len(r['options'])) for r in requests]):
        loads = [[v for v in world] for world in worlds]
        value = 0
        for r, choice in zip(requests, choices):
            if choice >= 0:
                value += r['value']
                for load in loads:
                    for k, demand in enumerate(r['options'][choice]):
                        load[k] += demand
        if all(all(0 <= x <= c for x, c in zip(load, capacity)) for load in loads):
            if value > score:
                best, score = choices, value
    return score, best


def envelope_solver(capacity, worlds, requests):
    """Separate depth-first solver using only componentwise worst-case load."""
    residual = tuple(c - max(w[k] for w in worlds) for k, c in enumerate(capacity))
    best = [0, tuple([-1] * len(requests))]
    def visit(i, room, value, chosen):
        if i == len(requests):
            if value > best[0]:
                best[:] = value, tuple(chosen)
            return
        visit(i + 1, room, value, chosen + [-1])
        for j, demand in enumerate(requests[i]['options']):
            if all(d <= x for d, x in zip(demand, room)):
                visit(i + 1, tuple(x-d for x, d in zip(room, demand)),
                      value + requests[i]['value'], chosen + [j])
    visit(0, residual, 0, [])
    return tuple(best)


def greedy(capacity, worlds, requests):
    """Ordinary ACK-informed reservation allocator, fixed request/route order."""
    room = [c - max(w[k] for w in worlds) for k, c in enumerate(capacity)]
    score, chosen = 0, []
    for r in requests:
        choice = -1
        for j, demand in enumerate(r['options']):
            if all(d <= x for d, x in zip(demand, room)):
                room = [x-d for x, d in zip(room, demand)]
                score += r['value']
                choice = j
                break
        chosen.append(choice)
    return score, tuple(chosen)


def main():
    # Four coordinates: link A, CPU A, link B, CPU B. Both outcomes are
    # disclosed possibilities, never the simulator's hidden realized outcome.
    cases = [dict(name='flexible_before_constrained', capacity=[10]*4,
                  worlds=[[0]*4], requests=[
                      dict(value=1, options=[[6,6,0,0],[0,0,6,6]]),
                      dict(value=1, options=[[6,6,0,0]])]),
             dict(name='uncertain_migration', capacity=[10]*4,
                  worlds=[[6,6,0,0],[0,0,6,6]], requests=[
                      dict(value=1, options=[[6,6,0,0],[0,0,6,6]])])]
    rng = random.Random(20261103)
    for n in range(100):
        worlds = [[rng.randrange(7) for _ in range(4)] for _ in range(3)]
        requests = []
        for _ in range(4):
            a, b = rng.randrange(1,7), rng.randrange(1,7)
            options = [[a,b,0,0],[0,0,a,b]]
            if rng.random() < .5:
                options = options[rng.randrange(2):][:1]
            requests.append(dict(value=rng.randrange(1,6), options=options))
        cases.append(dict(name=f'generated_{n}', capacity=[10]*4,
                          worlds=worlds, requests=requests))
    results = []
    for case in cases:
        args = case['capacity'], case['worlds'], case['requests']
        exact, allocation = reference(*args)
        reduced, _ = envelope_solver(*args)
        ordinary, _ = greedy(*args)
        assert exact == reduced, case['name']
        assert exact >= ordinary, case['name']
        results.append(dict(**case, exact_value=exact, envelope_value=reduced,
                            greedy_value=ordinary, exact_assignment=allocation))
    assert results[0]['exact_value'] == 2 and results[0]['greedy_value'] == 1
    assert results[1]['exact_value'] == 0
    summary = dict(cases=len(cases), exact_envelope_equal=len(results),
                   greedy_suboptimal_cases=sum(r['greedy_value'] < r['exact_value'] for r in results),
                   seed=20261103, novelty_established=False,
                   note='One-step robust assignment only; not a dynamic MPC reproduction.')
    root = Path(__file__).parent
    output = dict(summary=summary, results=results)
    (root/'results.json').write_text(json.dumps(output, indent=2)+'\n')
    hashes = {p: hashlib.sha256((root/p).read_bytes()).hexdigest()
              for p in ['experiment.py', 'results.json', 'README.md']}
    (root/'verification.json').write_text(json.dumps(dict(summary=summary, sha256=hashes), indent=2)+'\n')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
