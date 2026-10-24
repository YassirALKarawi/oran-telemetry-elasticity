"""Version 2 controlled ablations of a synthetic tandem-queue telemetry pilot.
Standard library only. No O-RAN protocol implementation or claimed guarantee.
"""
import argparse
import hashlib
import json
import math
import random
import statistics as st
import unittest
from collections import deque
from pathlib import Path
from baseline.simulate import trace, allocate, DEADLINES, select_report, predicted

CONFIGS = {
    "legacy_periodic": ("periodic", False, False),
    "legacy_oldest": ("oldest", False, False),
    "legacy_impact": ("impact", False, False),
    "scheduler_only": ("periodic", True, False),
    "predictor_only": ("periodic", False, True),
    "modern_periodic": ("periodic", True, True),
    "modern_oldest": ("oldest", True, True),
    "modern_risk": ("risk", True, True),
}


def forecast(report, t, modern):
    if not modern:
        return predicted((report["q"], report["arrival"], report["capacity"], report["time"]), t)
    age = t - report["time"]
    return [max(0, report["q"][s] + age * (report["arrival"][s] - report["service"][s]))
            for s in range(2)]


def choose(policy, reports, t, n):
    if policy != "risk":
        old = [(r["q"], r["arrival"], r["capacity"], r["time"]) for r in reports]
        return select_report(policy, old, t, n)
    scores = []
    for r in reports:
        age = t - r["time"]
        q = forecast(r, t, True)
        # A dispersion-based priority proxy, NOT a calibrated confidence bound.
        score = sum(math.sqrt(age * r["variance"][s] + 1) / DEADLINES[s]
                    * (1 + q[s] / max(1, r["capacity"])) for s in range(2))
        scores.append(score + .01 * age)  # fixed anti-starvation term
    return max(range(3), key=lambda i: (scores[i], -i))


def schedule(queues, weights, capacity, work_conserving):
    reserved = allocate(weights, capacity)
    taken = [min(len(queues[s]), reserved[s]) for s in range(2)]
    if work_conserving:
        for _ in range(capacity - sum(taken)):
            eligible = [s for s in range(2) if len(queues[s]) > taken[s]]
            if not eligible:
                break
            s = min(eligible, key=lambda s: (queues[s][taken[s]][1] + DEADLINES[s], s))
            taken[s] += 1
        assert sum(taken) == min(capacity, sum(map(len, queues)))
    assert sum(taken) <= capacity
    return taken


def run(events, name, seed=0, warmup=300, measure=3000, delay=3, loss=.05):
    policy, work, modern = CONFIGS[name]
    cohort_end = warmup + measure
    assert len(events) >= cohort_end + max(DEADLINES)
    queues = [[deque(), deque()] for _ in range(3)]
    reports = [dict(q=[0, 0], arrival=[.9, 2.1], service=[2.5, 2.5],
                    variance=[1, 1], capacity=5, time=0) for _ in range(3)]
    history = [deque(maxlen=20) for _ in range(3)]
    rng = random.Random(seed + 100000)
    loss_flags = [rng.random() < loss for _ in range((len(events) + 4) // 5)]
    pending, samples = [], []
    weights = [[1, 1] for _ in range(3)]
    generated, completed, late = [0, 0], [0, 0], [0, 0]
    delays, admitted = [[], []], [0, 0]
    qsum = attempts = delivered = useful = discarded = 0
    for t, (arrivals, capacities) in enumerate(events):
        waiting = []
        for at, i, payload in pending:
            if at <= t:
                delivered += 1
                if payload["time"] >= reports[i]["time"]:
                    reports[i] = payload
                    useful += 1
                else:
                    discarded += 1
            else:
                waiting.append((at, i, payload))
        pending = waiting
        ingress = [[0, 0] for _ in range(3)]
        served = [[0, 0] for _ in range(3)]
        for s in range(2):
            generated[s] += arrivals[s]
            ingress[0][s] = arrivals[s]
            if warmup <= t < cohort_end:
                admitted[s] += arrivals[s]
            for k in range(arrivals[s]):
                queues[0][s].append(((s, t, k), t))
        if t % 5 == 0:
            i = choose(policy, reports, t, attempts)
            h = history[i]
            arrival = [st.fmean(x[0][s] for x in h) if h else [.9, 2.1][s] for s in range(2)]
            service = [st.fmean(x[1][s] for x in h) if h else 2.5 for s in range(2)]
            variance = [st.pvariance([x[0][s] - x[1][s] for x in h]) if len(h) > 1 else 1
                        for s in range(2)]
            payload = dict(q=[len(q) for q in queues[i]], arrival=arrival,
                           service=service, variance=variance, capacity=capacities[i], time=t)
            if not loss_flags[attempts]:
                pending.append((t + delay, i, payload))
            attempts += 1
            weights = [[(1 + x) / DEADLINES[s] for s, x in enumerate(forecast(r, t, modern))]
                       for r in reports]
        for i in (2, 1, 0):
            taken = schedule(queues[i], weights[i], capacities[i], work)
            for s in range(2):
                served[i][s] = taken[s]
                for _ in range(taken[s]):
                    packet = queues[i][s].popleft()
                    if i < 2:
                        queues[i + 1][s].append(packet)
                        ingress[i + 1][s] += 1
                    else:
                        completed[s] += 1
                        birth = packet[1]
                        if warmup <= birth < cohort_end:
                            d = t - birth + 1
                            delays[s].append(d)
                            late[s] += d > DEADLINES[s]
        for i in range(3):
            history[i].append((ingress[i], served[i]))
        if warmup <= t < cohort_end:
            qsum += sum(len(q) for pair in queues for q in pair)
        assert sum(generated) == sum(completed) + sum(len(q) for pair in queues for q in pair)
    # Entire measured cohort has now reached its deadline. Unfinished measured
    # packets are confirmed violations, not unobserved successes.
    unfinished = [sum(warmup <= birth < cohort_end for pair in queues for _, birth in pair[s])
                  for s in range(2)]
    rates = [(late[s] + unfinished[s]) / max(1, admitted[s]) for s in range(2)]
    percentile = lambda d: sorted(d)[max(0, math.ceil(.99 * len(d)) - 1)] if d else None
    return dict(config=name, seed=seed, arrivals=admitted, violation=rates,
                late_completed=late, unfinished=unfinished,
                completed_delay_p99=[percentile(d) for d in delays],
                mean_backlog=qsum / measure, requests=attempts, delivered=delivered,
                accepted=useful, discarded_out_of_order=discarded,
                pending_reports=len(pending),
                trace_hash=hashlib.sha256(json.dumps(events).encode()).hexdigest())


def bootstrap_ci(values, seed=9000, repeats=2000):
    rng = random.Random(seed)
    n = len(values)
    means = sorted(st.fmean(values[rng.randrange(n)] for _ in range(n)) for _ in range(repeats))
    return [means[int(.025 * repeats)], means[min(repeats - 1, int(.975 * repeats))]]


class Checks(unittest.TestCase):
    def test_work_conservation(self):
        q = [deque(), deque([(1, 0)] * 10)]
        self.assertEqual(schedule(q, [9, 1], 5, True), [0, 5])
        self.assertLess(sum(schedule(q, [9, 1], 5, False)), 5)

    def test_forecast_uses_service(self):
        r = dict(q=[10, 10], arrival=[1, 2], service=[1, 2], time=0, capacity=5)
        self.assertEqual(forecast(r, 100, True), [10, 10])

    def test_budget_and_reproducibility(self):
        e = trace(11, 100, "nominal")
        rs = [run(e, c, warmup=10, measure=50, seed=11) for c in CONFIGS]
        self.assertEqual(len({r["requests"] for r in rs}), 1)
        self.assertEqual(len({r["delivered"] for r in rs}), 1)
        self.assertEqual(len({r["trace_hash"] for r in rs}), 1)
        self.assertEqual(rs[-1], run(e, "modern_risk", warmup=10, measure=50, seed=11))

    def test_unfinished_are_violations(self):
        e = [([10, 10], [0, 0, 0])] * 100
        r = run(e, "modern_risk", warmup=10, measure=50)
        self.assertEqual(r["violation"], [1, 1])

    def test_empty_and_minimum_delay(self):
        e = [([0, 0], [5, 5, 5])] * 100
        r = run(e, "modern_risk", warmup=10, measure=50, delay=1000)
        self.assertEqual(r["delivered"], 0)
        e[10] = ([1, 0], [5, 5, 5])
        r = run(e, "modern_risk", warmup=10, measure=50)
        self.assertEqual(r["completed_delay_p99"][0], 3)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--test", action="store_true")
    p.add_argument("--seeds", type=int, default=20)
    p.add_argument("--measure", type=int, default=3000)
    p.add_argument("--output", default="results_v2.json")
    a = p.parse_args()
    if a.test:
        unittest.main(argv=["experiment.py"])
        return
    if a.seeds < 2 or a.measure < 1:
        p.error("At least two seeds and a positive measurement horizon required")
    runs, summaries, comparisons = [], [], []
    cases = [("nominal", 3, .05), ("bursty_transport", 3, .05),
             ("bursty_compute", 3, .05), ("bursty_transport", 9, .15)]
    for scenario, delay, loss in cases:
        label = f"{scenario}_delay{delay}_loss{loss}"
        for seed in range(1000, 1000 + a.seeds):
            events = trace(seed, 300 + a.measure + 40, scenario)
            for config in CONFIGS:
                runs.append(dict(case=label, **run(events, config, seed=seed,
                                                   measure=a.measure, delay=delay, loss=loss)))
        for config in CONFIGS:
            rows = [r for r in runs if r["case"] == label and r["config"] == config]
            summaries.append(dict(case=label, config=config,
                                  mean_violations=[st.fmean(r["violation"][s] for r in rows) for s in range(2)],
                                  mean_backlog=st.fmean(r["mean_backlog"] for r in rows)))
        for comparator in ("legacy_periodic", "modern_periodic", "modern_oldest"):
            by_seed = {r["seed"]: r for r in runs if r["case"] == label and r["config"] == comparator}
            differences = [r["violation"][0] - by_seed[r["seed"]]["violation"][0]
                           for r in runs if r["case"] == label and r["config"] == "modern_risk"]
            comparisons.append(dict(case=label, comparison="modern_risk minus " + comparator,
                                    mean_difference=st.fmean(differences), paired_bootstrap_ci95=bootstrap_ci(differences)))
        print(label, "completed", flush=True)
    out = dict(status="synthetic_pilot_v2_not_publication_ready", seed_start=1000,
               seeds=a.seeds, warmup=300, measure=a.measure, followup=40,
               slot_ms=20, report_interval=5, summaries=summaries,
               paired_comparisons=comparisons, runs=runs)
    Path(a.output).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
