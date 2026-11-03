# Delayed-command mechanism experiment

Date: 3 November 2026. Deterministic simulation only. No novelty, statistical
superiority, physical deployment or O-RAN interface implementation is claimed.

## Model and execution

```sh
python3 -m unittest discover -s ack_allocation -p 'test_*.py' -v
python3 ack_allocation/experiment.py
```

Python standard library only. Every route consumes one link reservation and
one processing reservation, each of capacity 10. Requests reserve 6 units
unless explicitly specified otherwise. Resource units and time ticks are
abstract; costs, energy, radio channel behavior and packet latency are absent.
There are no departures or resubmission of deferred requests in this small
experiment. Atomic resource application is an explicit simulator assumption,
not an asserted SDN/E2 protocol capability.

Reports contain timestamped physical load and completed-command identifiers.
The controller only receives reports and acknowledgements at delivery time;
execution timers and injected-failure flags belong exclusively to the simulator.
Older reports are ignored. A success acknowledgement retains the reservation
until a newer snapshot covers it. Failed commands release reservations only
after delivered failure acknowledgement or reconciliation by a fresh snapshot.
No timeout is interpreted as proof of failure.

The physical actuator rejects infeasible commands. Thus a capacity-conflict
attempt is counted separately from actual resource over-allocation, which is
prevented by the actuator for every policy. Comparing only actual overloads
would conceal the ineffective commands.

## Policies

- reports_only: uses the last delivered snapshot; deliberately incomplete
  diagnostic comparator.
- issue_ledger: also reserves positive resource deltas for issued commands;
  ignores acknowledgements, but reconciles new reports.
- ack_aware: conventional reservation bookkeeping with failure acknowledgements.
- causal_reference: an explicitly identical conventional-rule control using
  the same implementation as ack_aware. It is NOT an independently reproduced
  published algorithm, an independent verification implementation, or another
  competitive baseline. Equality is expected by construction and checks the
  labels, not novelty.

## Executed results

Six hand-built scenarios, four policy labels: 24 deterministic executions.
Nine tests cover conflict rejection versus actual overload, alternative-route
allocation, zero-delay decision equivalence, snapshot double counting, retained
success reservations, missing/confirmed failure acknowledgements, conventional
rule equivalence, causal timestamps, stale reports and duplicate identifiers.

Each table cell is applied requests / capacity-conflict attempts / deferred
requests. All scenarios offer two requests.

| Scenario | reports_only | issue_ledger | ack_aware |
|---|---|---|---|
| One route, delayed execution | 1 / 1 / 0 | 1 / 0 / 1 | 1 / 0 / 1 |
| Two alternative routes | 1 / 1 / 0 | 2 / 0 / 0 | 2 / 0 / 0 |
| Zero execution/ACK delay, fresh report | 1 / 0 / 1 | 1 / 0 / 1 | 1 / 0 / 1 |
| Fresh snapshot before ACK | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 |
| Injected first-command failure, ACK delivered | 1 / 0 / 0 | 0 / 0 / 1 | 1 / 0 / 0 |
| Injected failure, ACK absent, no new report | 1 / 0 / 0 | 0 / 0 / 1 | 0 / 0 / 1 |

The missing-ACK case exposes the cost of conservative reservations: the
controller cannot know the first command failed, so it defers the second.
reports_only happens to benefit in that particular case; its result does not
make it generally safe or efficient. In the single-route successful case,
ledger bookkeeping removes a conflicting attempt but serves the same number
of requests. The alternative-route case admits the second request on a
different link/processing pair. No improvement percentage is inferred from
these hand-built scenarios.

## Scientific decision

The mechanism is demonstrable, but acknowledgement-aware bookkeeping alone
does not pass a novelty gate. The reference is the same conventional rule,
and the issue ledger already resolves the main successful-command example.
A new reinforcement-learning campaign is not justified by this experiment.

Next gate: specify and solve the coupled multi-resource decision under a
nontrivial set of possible command outcomes/application orders, then compare
against an ordinary ACK-aware allocator and a matched robust/MPC allocator.
This requires independently implemented comparators, full-text closest-work
review and a defensible protocol model. If the benefit disappears against
those comparators, reject the candidate contribution. The completed PRORL
baseline and previous negative diagnostics remain unchanged.

Raw events, delivered-message records, outcomes and scenario parameters are
in results.json. verification.json records executed checks and file hashes.
