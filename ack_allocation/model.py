"""Causal deterministic mechanism experiment, not a novel allocator.

Resources are abstract reservations. Physical actuators reject conflicting
commands atomically; a conflict attempt never becomes real over-allocation.
"""
from dataclasses import dataclass
import heapq


@dataclass(frozen=True)
class Scenario:
    name: str
    routes: int = 1
    execution_delay: int = 3
    acknowledgement_delay: int | None = 3
    report_times: tuple = (0,)
    report_delay: int = 0
    arrivals: tuple = ((0, 6), (1, 6))
    fail_first: bool = False
    horizon: int = 12


class Controller:
    """Receives delivered messages; cannot inspect simulator state or timers."""
    def __init__(self, policy, capacities):
        if policy not in ('reports_only', 'issue_ledger', 'ack_aware', 'causal_reference'):
            raise ValueError(policy)
        self.policy = policy
        self.capacities = capacities.copy()
        self.report_load = {k: 0 for k in capacities}
        self.report_time = -1
        self.covered = set()
        self.issued = {}
        self.failures = set()
        self.received = []

    def report(self, now, timestamp, load, completed):
        assert timestamp <= now
        self.received.append(('report', now, timestamp))
        if timestamp <= self.report_time:
            return
        self.report_time = timestamp
        self.report_load = load.copy()
        self.covered = set(completed)

    def acknowledge(self, now, command_id, success):
        assert command_id in self.issued
        self.received.append(('ack', now, command_id))
        if self.policy in ('ack_aware', 'causal_reference') and not success:
            self.failures.add(command_id)
        # Success acknowledgements do NOT release the resource reservation.

    def committed(self):
        load = self.report_load.copy()
        if self.policy != 'reports_only':
            for cid, (resources, amount) in self.issued.items():
                if cid not in self.covered and cid not in self.failures:
                    for resource in resources:
                        load[resource] += amount
        return load

    def decide(self, cid, amount, alternatives):
        if cid in self.issued:
            raise ValueError('Duplicate command identifier')
        load = self.committed()
        for resources in alternatives:
            if all(load[k] + amount <= self.capacities[k] for k in resources):
                self.issued[cid] = (tuple(resources), amount)
                return tuple(resources)
        return None


def run(scenario, policy):
    s = scenario
    assert s.execution_delay >= 0 and s.report_delay >= 0
    assert s.acknowledgement_delay is None or s.acknowledgement_delay >= 0
    alternatives = [(f'link_{i}', f'cpu_{i}') for i in range(s.routes)]
    capacities = {k: 10 for path in alternatives for k in path}
    controller = Controller(policy, capacities)
    actual = {k: 0 for k in capacities}
    completed = {}
    events, serial, trace = [], 0, []
    def schedule(t, priority, kind, payload):
        nonlocal serial
        serial += 1
        heapq.heappush(events, (t, priority, serial, kind, payload))
    for t in s.report_times:
        schedule(t, 1, 'snapshot', None)
    for cid, (t, amount) in enumerate(s.arrivals):
        schedule(t, 4, 'arrival', (cid, amount))
    counts = dict(offered=len(s.arrivals), issued=0, deferred=0, applied=0,
                  capacity_conflicts=0, injected_failures=0, actual_overloads=0)
    while events:
        now, _, _, kind, payload = heapq.heappop(events)
        if now > s.horizon:
            break
        if kind == 'snapshot':
            schedule(now+s.report_delay, 2, 'report', (now, actual.copy(), completed.copy()))
        elif kind == 'report':
            controller.report(now, *payload)
        elif kind == 'ack':
            controller.acknowledge(now, *payload)
        elif kind == 'arrival':
            cid, amount = payload
            path = controller.decide(cid, amount, alternatives)
            counts['deferred' if path is None else 'issued'] += 1
            if path is not None:
                schedule(now+s.execution_delay, 0, 'apply', (cid, amount, path))
            trace.append(dict(time=now, event=kind, request=cid, route=path,
                              controller_commitment=controller.committed()))
        elif kind == 'apply':
            cid, amount, path = payload
            injected = s.fail_first and cid == 0
            feasible = all(actual[k]+amount <= capacities[k] for k in path)
            success = feasible and not injected
            if success:
                for k in path:
                    actual[k] += amount
                counts['applied'] += 1
            elif injected:
                counts['injected_failures'] += 1
            else:
                counts['capacity_conflicts'] += 1
            completed[cid] = success
            if s.acknowledgement_delay is not None:
                schedule(now+s.acknowledgement_delay, 3, 'ack', (cid, success))
            trace.append(dict(time=now, event=kind, request=cid, success=success))
        assert all(0 <= actual[k] <= capacities[k] for k in actual)
    assert counts['issued'] + counts['deferred'] == counts['offered']
    return dict(scenario=s.name, policy=policy, **counts, final_load=actual,
                trace=trace, received_messages=controller.received,
                outstanding_at_horizon=counts['issued']-len(completed))
