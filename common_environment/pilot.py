"""One paired development trace for the synthetic tandem-queue controller."""
import csv
import hashlib
import json
import math
import random
import statistics
import sys
from collections import deque
from pathlib import Path
from time import perf_counter_ns

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from baseline.simulate import DEADLINES, allocate, trace
from elastic import solve_elastic
from engine_v4 import schedule

SEED, HORIZON, PERIOD, REPORT_DELAY, COMMAND_DELAY = 74103, 360, 5, 3, 10
OUT = Path(__file__).resolve().parent
POLICIES = ("thesis", "greedy")


def greedy(reports):
    # Allocate immediate service to the observed backlog, prioritizing deadlines.
    # Equal service scores prefer fewer extra units and then the lower share index.
    best = None
    for k in range(1, 20):
        weights = [k / 20, 1 - k / 20]
        extras, score = [], 0
        for i, report in enumerate(reports):
            options = []
            for extra in range(1 if i == 0 else 4):
                quota = allocate(weights, report["capacity"] + extra)
                benefit = sum(min(q, n) / d for q, n, d in zip(report["q"], quota, DEADLINES))
                options.append((benefit, -extra))
            benefit, neg_extra = max(options)
            score += benefit
            extras.append(-neg_extra)
        ranking = (-score, sum(extras), k)
        if best is None or ranking < best[0]:
            best = ranking, extras, [weights[:] for _ in reports]
    return best[1:]


def choose(name, reports, t, previous):
    if name == "thesis":
        extra, weights, _ = solve_elastic(reports, t, previous, maximum=3, delay=COMMAND_DELAY)
    else:
        extra, weights = greedy(reports)
    check_action(extra, weights)
    return extra, weights


def check_action(extra, weights):
    assert len(extra) == 3
    assert extra[0] == 0 and all(type(n) is int and 0 <= n <= 3 for n in extra)
    assert len(weights) == 3 and all(w == weights[0] for w in weights)
    assert any(weights[0] == [k / 20, 1 - k / 20] for k in range(1, 20))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def run(name, events, drop, *, controller=None, write_logs=True):
    queues = [[deque(), deque()] for _ in range(3)]
    reports = [dict(q=[0, 0], arrival=[.9, 2.1], service=[2.5, 2.5], variance=[1, 1],
                    capacity=5, time=0) for _ in range(3)]
    history = [deque(maxlen=20) for _ in reports]
    active = previous = [0, 0, 0]
    weights = [[1, 1] for _ in reports]
    commands, messages, packets, epochs, checks = {}, {}, {}, [], []
    service, supply = [0]*3, [0]*3
    units = switches = delivered = 0
    total_cost = 0.0
    interval_cost = 0.0
    for t, (arrivals, base) in enumerate(events):
        switch_before = switches
        if t in commands:
            extra, weights, log = commands.pop(t)
            switches += sum(abs(a-b) for a,b in zip(extra, active))
            active = extra
            log["applied"] = t
        if t in messages:
            stage, reports_new = messages.pop(t)
            reports[stage] = reports_new
        capacity = [a+b for a,b in zip(base,active)]
        units += sum(active)
        ingress = [list(arrivals), [0, 0], [0, 0]]
        served = [[0, 0] for _ in reports]
        for s, count in enumerate(arrivals):
            for n in range(count):
                key = (s,t,n)
                packets[key] = None
                queues[0][s].append((key,t))
        if t % PERIOD == 0:
            epoch = t // PERIOD
            stage = epoch % 3
            h = history[stage]
            if not drop[epoch]:
                messages[t+REPORT_DELAY] = stage, dict(
                    q=[len(q) for q in queues[stage]], time=t, capacity=base[stage],
                    arrival=[statistics.fmean(x[0][s] for x in h) if h else [.9,2.1][s] for s in range(2)],
                    service=[statistics.fmean(x[1][s] for x in h) if h else 2.5 for s in range(2)],
                    variance=[statistics.pvariance(x[0][s]-x[1][s] for x in h) if len(h)>1 else 1 for s in range(2)])
            signature = digest([reports,t,previous])
            # Both adapters are exercised on identical inputs. Only the assigned action executes.
            actions, times = {}, {}
            for policy in (POLICIES if write_logs and controller is None else (name,)):
                start = perf_counter_ns()
                if controller is None:
                    actions[policy] = choose(policy,reports,t,previous)
                else:
                    actions[policy] = controller.act(reports, t, previous, interval_cost)
                    check_action(*actions[policy])
                times[policy] = perf_counter_ns()-start
                assert digest([reports,t,previous]) == signature
            extra, target_weights = actions[name]
            log = dict(issue=t, due=t+COMMAND_DELAY, applied=None, input_sha256=signature,
                       report_ages=[t-r["time"] for r in reports], actions=actions, decision_ns=times)
            epochs.append(log)
            commands[t+COMMAND_DELAY] = extra,target_weights,log
            previous = extra
            interval_cost = 0.0
        for i in (2,1,0):
            served[i] = schedule(queues[i],weights[i],capacity[i],True)
            assert sum(served[i]) <= capacity[i]
            service[i] += sum(served[i])
            supply[i] += capacity[i]
            for s, count in enumerate(served[i]):
                for _ in range(count):
                    packet = queues[i][s].popleft()
                    if i < 2:
                        queues[i+1][s].append(packet)
                        ingress[i+1][s] += 1
                    else:
                        key = packet[0]
                        assert packets[key] is None
                        packets[key] = t
                        delivered += 1
        for i in range(3):
            history[i].append((ingress[i],served[i]))
        pending = sum(len(q) for stage in queues for q in stage)
        assert len(packets) == delivered + pending
        slot_cost = pending / 20 + sum(active) / 5 + (switches-switch_before) / 20
        interval_cost += slot_cost
        total_cost += slot_cost
        checks.append([t,len(packets),delivered,pending,capacity,served])
    if controller is not None:
        controller.finish(interval_cost)
    unfinished = {pkt[0] for stage in queues for q in stage for pkt in q}
    assert unfinished == {key for key,end in packets.items() if end is None}
    assert all(e["applied"] == (e["due"] if e["due"] < len(events) else None) for e in epochs)
    delays = [end-birth+1 for (_,birth,_),end in packets.items() if end is not None]
    mature = [(key,end) for key,end in packets.items() if key[1]+DEADLINES[key[0]] <= len(events)]
    misses = sum(end is None or end-key[1]+1 > DEADLINES[key[0]] for key,end in mature)
    if write_logs:
        with (OUT/f"{name}_packets.csv").open("w") as f:
            writer = csv.writer(f)
            writer.writerow(("class","birth_slot","sequence","delivered_slot"))
            writer.writerows((*key,end) for key,end in packets.items())
        (OUT/f"{name}_audit.json").write_text(json.dumps(dict(epochs=epochs,slots=checks),separators=(",",":")))
    return dict(total_cost=total_cost, offered=len(packets),admitted=len(packets),delivered=delivered,lost=0,outstanding=len(unfinished),
                mature_packets=len(mature),deadline_misses=misses,delivered_p99_slots=sorted(delays)[math.ceil(.99*len(delays))-1],
                extra_unit_slots=units,switching_units=switches,stage_service=service,stage_supply=supply,
                decision_epochs=len(epochs),paired_observation_checks=len(epochs) if write_logs and controller is None else 0,end_state_checked=True)


if __name__ == "__main__":
    events = trace(SEED,HORIZON,"bursty_transport")
    rng = random.Random(SEED+100000)
    drop = [rng.random()<.05 for _ in range(0,HORIZON,PERIOD)]
    raw = dict(events=events,report_loss=drop)
    (OUT/"trace.json").write_text(json.dumps(raw,separators=(",",":")))
    results = {name:run(name,events,drop) for name in POLICIES}
    assert results["thesis"]["offered"] == results["greedy"]["offered"]
    (OUT/"results.json").write_text(json.dumps(dict(seed=SEED,horizon=HORIZON,trace_sha256=digest(raw),
                                                      policies=results),indent=2)+"\n")
