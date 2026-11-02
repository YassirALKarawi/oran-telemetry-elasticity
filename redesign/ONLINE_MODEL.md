# Causal reservation model and conditional service guarantee

## Information and control authority

Packet p is observed at release r_p with inclusive end-to-end deadline d_p. It requires one service unit at each of three stages, in strictly increasing integer slots. The controller sees only packets already released, its immutable reservations, and its own previously issued capacity leases. It does not receive future arrivals or future realized capacities. Each stage has a contractual service floor b_i. Radio capacity cannot be expanded. Transport and compute admit up to E concurrent additional units.

A unit lease issued at r_p activates at r_p+L and ends no earlier than r_p+L+M. L is the assumed actuation delay and M is the minimum lease duration. These are modeled commitments. There is no implemented E2, SDN, or CPU provisioning interface in this prototype. Admission computation is assumed to finish before the first reserved slot, which must be checked separately when assigning physical slot durations.

## Decision rule

Let U_i(t) be already reserved service and E_i(t) the number of active committed lease units. For every candidate triple r_p<=t_0<t_1<t_2<=d_p, test U_i(t_i)+1<=b_i+E_i(t_i). If a stage needs another unit, a lease may be issued only for i>0 and t_i>=r_p+L. Its interval is [r_p+L,max(r_p+L+M,t_i+1)). Every slot in that interval must respect the concurrent expansion limit. An infeasible candidate is discarded.

Among feasible candidates, minimize incremental lease unit-slots, then completion time, then the service-slot triple. Accept and append its reservations and leases without modifying earlier commitments. Reject if no candidate is feasible. This greedy rule is a causal baseline/prototype. No global optimality or novelty is claimed for it.

## Conditional guarantee and proof

Assume: (1) actual base service at every scheduled slot is at least b_i, (2) all leases activate by their modeled start and persist through their modeled end, (3) each packet needs exactly the modeled service units, (4) reserved execution is enforced, and (5) admission computation and dispatch fit the timing model. Then every accepted packet completes by its deadline.

Proof. Initially the empty calendar respects every capacity. At acceptance, each new service reservation fits existing service plus a feasible new lease if needed. Each new lease respects the concurrency limit throughout its lifetime. Earlier leases and reservations remain unchanged. Induction over arrivals therefore gives U_i(t)<=b_i+E_i(t) for all scheduled slots. Under assumptions (1)--(5), every reserved unit executes. The strict slot ordering gives stage precedence, and the final slot is no later than d_p. This proves the stated conditional result. It does not guarantee acceptance of arbitrary offered traffic, robustness to breached service floors, or a stochastic reliability level in a real network.

## Execution verification and failure reporting

`execute_certificate` is separate from candidate selection. It reads realized service floors only when executing scheduled actions. A missing predecessor or unavailable capacity causes the packet to fail rather than silently being counted as served. The result separately records offered, admitted, rejected, timely completed, failed admitted, and observed floor-breach slots. The floor-breach test intentionally invalidates the guarantee assumptions and verifies that failures are visible.

The causal-prefix test changes later traffic and verifies that earlier commitments remain identical. Fifty randomized cases check execution under the contractual floors. Existing finite-instance tests compare the independent MILP reference with exhaustive enumeration on 60 instances.

## Comparison scope

The synthetic experiment uses 20 seeds, four delays, 36 packets per trace, fixed floors (2,1,1), maximum expansion 2 per downstream stage, and minimum lease duration 5. It runs the causal lease policy, the same reservation policy without expansion, and a fully provisioned static capacity benchmark. The latter starts with downstream floors (3,3), so it is a capability/cost comparator, not an equal-budget superiority test. The offline optimum uses all future packet releases and bounds attainable admissions with maximum expansion after the same delay. It is not a causal competitor.

All rejected packets remain in the offered denominator. Lease cost includes the complete committed interval even if it extends beyond the arrival horizon. A positive efficiency or journal-level novelty claim additionally requires matched service/budget comparisons and faithful external algorithms.

## Relation to experimental radio data

The inspected ColO-RAN records do not establish deterministic service floors. Observed throughput depends on offered traffic, scheduler decisions, and channel quality. In particular, throughput under low offered load is not available capacity. Therefore the synthetic guarantee is not described as experimentally verified O-RAN reliability. Admission/resource reservation is established prior art, including https://arxiv.org/abs/2203.09367 and https://arxiv.org/abs/1506.04330 . The specific technical novelty of a publishable redesign remains to be established.
