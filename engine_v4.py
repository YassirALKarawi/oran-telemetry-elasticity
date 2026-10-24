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
from elastic import solve_elastic

CONFIGS = {name: ("risk", True, True) for name in ("fixed", "always_on", "elastic_cap1", "elastic_cap3")}


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


def run(events, name, seed=0, warmup=300, measure=3000, delay=3, loss=.05, activation_delay=10):
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
    constrained_epochs = feasible_epochs = 0
    max_slack = 0.0
    extra = [0, 3, 3] if name == "always_on" else [0, 0, 0]
    previous = list(extra)
    commands = []
    unit_slots = switching_units = 0
    active_history = []
    for t, (arrivals, base_capacity) in enumerate(events):
        commands_waiting=[]
        for when, target, target_weights in commands:
            if when <= t:
                switching_units += sum(abs(extra[i]-target[i]) for i in range(3))
                extra = target
                weights = target_weights
            else:
                commands_waiting.append((when, target, target_weights))
        commands=commands_waiting
        capacities=[base_capacity[i]+extra[i] for i in range(3)]
        unit_slots += sum(extra)
        active_history.append(tuple(extra))
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
                           service=service, variance=variance, capacity=base_capacity[i], time=t)
            if not loss_flags[attempts]:
                pending.append((t + delay, i, payload))
            attempts += 1
            maximum = 1 if name == "elastic_cap1" else 3
            fixed = (0,0,0) if name == "fixed" else ((0,3,3) if name == "always_on" else None)
            target, target_weights, diagnostic = solve_elastic(
                reports,t,previous,maximum=maximum,delay=activation_delay,fixed=fixed)
            commands.append((t+activation_delay,target,target_weights))
            previous=target
            constrained_epochs += 1
            feasible_epochs += diagnostic["model_feasible"]
            max_slack=max(max_slack,diagnostic["maximum_normalized_slack"])
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
                extra_service_unit_slots=unit_slots, activation_switching_units=switching_units,
                abstract_cost=unit_slots+.25*switching_units,
                mean_extra_capacity=unit_slots/len(events),
                maximum_active_extra=max(sum(x) for x in active_history),
                first_nonzero_extra_slot=next((i for i,x in enumerate(active_history) if sum(x)>0),None),
                modeled_feasibility_checks=constrained_epochs,
                modeled_feasible_checks=feasible_epochs,
                maximum_modeled_normalized_slack=max_slack,
                late_completed=late, unfinished=unfinished,
                completed_delay_p99=[percentile(d) for d in delays],
                mean_backlog=qsum / measure, requests=attempts, delivered=delivered,
                accepted=useful, discarded_out_of_order=discarded,
                pending_reports=len(pending),
                trace_hash=hashlib.sha256(json.dumps(events).encode()).hexdigest())



