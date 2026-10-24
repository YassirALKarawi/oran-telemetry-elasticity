"""Reproducible abstract O-RAN telemetry pilot. Standard library only.

This is a packet-tandem abstraction, not an E2/SDN implementation, NR PHY,
or a solver with formal QoS guarantees. Policy superiority is not assumed.
"""
import argparse
import hashlib
import json
import math
import random
import statistics
import unittest
from collections import deque
from pathlib import Path

STAGES = ("radio", "transport", "compute")
DEADLINES = (15, 40)  # slots, synthetic targets rather than standard URLLC claims
BASE_CAPACITY = (5, 5, 5)  # abstract packets processed per slot
POLICIES = ("periodic", "oldest", "impact")


def trace(seed, steps, scenario):
    """Pre-generate exogenous events once; every policy gets the same trace."""
    rng = random.Random(seed)
    events = []
    for t in range(steps):
        burst = scenario != "nominal" and 180 <= t % 600 < 290
        rates = (1.8, 3.8) if burst else (0.9, 2.1)
        arrivals = []
        for rate in rates:
            # Poisson draw using Knuth's method.
            product, k = 1.0, 0
            while product > math.exp(-rate):
                product *= rng.random()
                k += 1
            arrivals.append(k - 1)
        capacities = [max(1, c + rng.choice((-1, 0, 0, 1))) for c in BASE_CAPACITY]
        if scenario == "bursty_transport" and 170 <= t % 600 < 310:
            capacities[1] = 3
        if scenario == "bursty_compute" and 170 <= t % 600 < 310:
            capacities[2] = 3
        events.append((arrivals, capacities))
    return events


def allocate(weights, capacity):
    """Integer weighted allocation. Does not inspect actual hidden queues."""
    total = sum(weights)
    if total == 0:
        return [0] * len(weights)
    raw = [capacity * w / total for w in weights]
    allocation = [int(x) for x in raw]
    order = sorted(range(len(raw)), key=lambda i: (raw[i] - allocation[i], -i), reverse=True)
    for i in order[:capacity - sum(allocation)]:
        allocation[i] += 1
    assert sum(allocation) == capacity
    return allocation


def predicted(report, t):
    q, rate, capacity, observed_at = report
    age = t - observed_at
    # Approximate unobserved growth; deliberately no access to actual queue state.
    return [max(0.0, q[s] + age * (rate[s] - capacity / 2)) for s in range(2)]


def select_report(policy, reports, t, request_number):
    if policy == "periodic":
        return request_number % 3
    if policy == "oldest":
        return max(range(3), key=lambda i: (t - reports[i][3], -i))
    scores = []
    for report in reports:
        q, rate, capacity, timestamp = report
        age = t - timestamp
        estimate = predicted(report, t)
        # Decision-impact heuristic: freshness uncertainty weighted by pressure.
        pressure = sum(estimate[s] / DEADLINES[s] for s in range(2))
        uncertainty = age * (1 + sum(rate))
        scores.append(uncertainty * (1 + pressure) / max(1, capacity))
    return max(range(3), key=lambda i: (scores[i], -i))


def simulate(events, policy, report_delay=3, report_loss=0.0, seed=0):
    assert policy in POLICIES
    queues = [[deque(), deque()] for _ in STAGES]
    reports = [([0, 0], [0.9, 2.1], c, 0) for c in BASE_CAPACITY]
    pending = []
    ingress = [[0, 0] for _ in STAGES]
    history = [deque(maxlen=20) for _ in STAGES]
    loss_rng = random.Random(seed + 100000)
    # Report losses are determined by request index, not selected resource.
    loss_flags = [loss_rng.random() < report_loss for _ in range((len(events) + 4) // 5)]
    generated = [0, 0]
    completed = [0, 0]
    late_completed = [0, 0]
    delays = [[], []]
    backlog_sum = 0
    requested = delivered = 0
    next_id = 0
    allocations = [allocate([1, 1], c) for c in BASE_CAPACITY]
    for t, (arrivals, capacity) in enumerate(events):
        # Deliver only reports whose actual delivery time has arrived.
        remaining = []
        for delivery_at, stage, payload in pending:
            if delivery_at <= t:
                if payload[3] >= reports[stage][3]:
                    reports[stage] = payload
                delivered += 1
            else:
                remaining.append((delivery_at, stage, payload))
        pending = remaining
        ingress = [[0, 0] for _ in STAGES]
        for s in range(2):
            for _ in range(arrivals[s]):
                queues[0][s].append((next_id, t))
                next_id += 1
            generated[s] += arrivals[s]
            ingress[0][s] = arrivals[s]
        if t % 5 == 0:
            stage = select_report(policy, reports, t, requested)
            q = [len(queues[stage][s]) for s in range(2)]
            rate = [statistics.fmean(x[s] for x in history[stage]) if history[stage]
                    else reports[stage][1][s] for s in range(2)]
            payload = (q, rate, capacity[stage], t)
            if not loss_flags[requested]:
                pending.append((t + report_delay, stage, payload))
            requested += 1
            # Freeze ratios for the control interval. Absolute available capacity
            # is enforced by the local scheduler, not supplied to the controller.
            allocations = []
            for i in range(3):
                estimate = predicted(reports[i], t)
                allocations.append([(1 + estimate[s]) / DEADLINES[s] for s in range(2)])
        # Downstream-first update prevents a packet crossing multiple stages
        # in one slot and enforces a minimum of three processing slots.
        for stage in (2, 1, 0):
            budget = allocate(allocations[stage], capacity[stage])
            for s in range(2):
                served = min(budget[s], len(queues[stage][s]))
                for _ in range(served):
                    packet = queues[stage][s].popleft()
                    if stage == 2:
                        delay = t - packet[1] + 1
                        delays[s].append(delay)
                        completed[s] += 1
                        late_completed[s] += delay > DEADLINES[s]
                    else:
                        queues[stage + 1][s].append(packet)
                        ingress[stage + 1][s] += 1
        for i in range(3):
            history[i].append(tuple(ingress[i]))
        backlog_sum += sum(len(q) for pair in queues for q in pair)
        assert sum(generated) == sum(completed) + sum(len(q) for pair in queues for q in pair)
    end = len(events)
    overdue = [sum(end - birth > DEADLINES[s] for stage in queues for _, birth in stage[s])
               for s in range(2)]
    def percentile(values, fraction):
        return sorted(values)[max(0, math.ceil(len(values) * fraction) - 1)] if values else None
    # Completed delays alone are survivor-biased: overdue unfinished packets
    # are explicitly included in the observed violation accounting.
    return {
        "policy": policy, "generated": generated, "completed": completed,
        "late_completed": late_completed, "overdue_unfinished": overdue,
        "unfinished": [sum(len(stage[s]) for stage in queues) for s in range(2)],
        "observed_violation_rate": [(late_completed[s] + overdue[s]) / max(1, generated[s])
                                    for s in range(2)],
        "completed_delay_p95_slots": [percentile(d, .95) for d in delays],
        "completed_delay_p99_slots": [percentile(d, .99) for d in delays],
        "mean_backlog_packets": backlog_sum / end,
        "requests": requested, "delivered": delivered,
        "pending_reports": len(pending),
        "trace_sha256": hashlib.sha256(json.dumps(events).encode()).hexdigest(),
    }


class Tests(unittest.TestCase):
    def test_allocator(self):
        self.assertEqual(sum(allocate([2, 3], 17)), 17)
        self.assertEqual(allocate([0, 0], 10), [0, 0])

    def test_no_arrivals(self):
        result = simulate([([0, 0], [5, 5, 5])] * 40, "impact")
        self.assertEqual(result["completed"], [0, 0])

    def test_minimum_delay(self):
        result = simulate([([1, 0], [5, 5, 5])] + [([0, 0], [5, 5, 5])] * 10, "periodic")
        self.assertEqual(result["completed_delay_p95_slots"][0], 3)

    def test_equal_information_budget(self):
        events = trace(3, 200, "bursty_transport")
        results = [simulate(events, p, report_loss=.1, seed=3) for p in POLICIES]
        self.assertEqual(len({r["requests"] for r in results}), 1)
        self.assertEqual(len({r["delivered"] for r in results}), 1)
        self.assertEqual(len({r["trace_sha256"] for r in results}), 1)

    def test_reproducibility(self):
        events = trace(8, 100, "nominal")
        self.assertEqual(simulate(events, "impact"), simulate(events, "impact"))

    def test_delayed_reports(self):
        result = simulate(trace(2, 10, "nominal"), "periodic", report_delay=100)
        self.assertEqual(result["delivered"], 0)
        self.assertEqual(result["pending_reports"], 2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--steps", type=int, default=3000)
    parser.add_argument("--output", default="results.json")
    args = parser.parse_args()
    if args.test:
        unittest.main(argv=["simulate.py"], exit=False)
        return
    if args.steps <= 0 or args.seeds < 2:
        parser.error("Use positive steps and at least two seeds.")
    runs = []
    summary = []
    for scenario in ("nominal", "bursty_transport", "bursty_compute"):
        for seed in range(args.seeds):
            events = trace(seed, args.steps, scenario)
            for policy in POLICIES:
                runs.append(dict(scenario=scenario, seed=seed,
                                 **simulate(events, policy, report_loss=.05, seed=seed)))
        for policy in POLICIES:
            selected = [r for r in runs if r["scenario"] == scenario and r["policy"] == policy]
            values = [r["observed_violation_rate"][0] for r in selected]
            mean = statistics.fmean(values)
            # Descriptive normal-approximation CI across independent seeds.
            half = 1.96 * statistics.stdev(values) / math.sqrt(len(values))
            summary.append(dict(scenario=scenario, policy=policy,
                                sensitive_violation_mean=mean, ci95_half_width=half,
                                mean_backlog=statistics.fmean(r["mean_backlog_packets"] for r in selected)))
    output = dict(status="abstract_pilot_not_manuscript_results", seeds=args.seeds,
                  steps=args.steps, slot_ms=20, report_delay_slots=3,
                  report_loss_probability=.05, report_interval_slots=5,
                  summaries=summary, runs=runs)
    Path(args.output).write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
