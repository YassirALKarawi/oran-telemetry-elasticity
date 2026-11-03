# Joint allocation: independent exact-reference gate

3 November 2026. Abstract deterministic experiment, Python standard library.
Run `python3 ack_allocation/joint_gate/experiment.py` from repository root.
This extends the earlier mechanism diagnostic without altering its results.

## Decision and information

At a decision epoch, select at most one link/CPU route for each currently
available request, or reject it. Maximize the sum of admitted request values.
Every policy receives the same capacity, requests and finite set of possible
committed resource loads consistent with delivered information. The set is
an input assumption, not an inferred or calibrated uncertainty model. No
policy observes which pending-command outcome actually occurs.

For binary assignments x_ij, route demand vectors d_ij, possible committed
loads b_s and capacity C, the problem is:

    maximize sum_i,j value_i x_ij
    subject to sum_j x_ij <= 1
               b_s,k + sum_i,j d_ij,k x_ij <= C_k for every s,k.

Demands and possible loads are nonnegative. Complete route reservation is
atomic. The four resources are link A, CPU A, link B, CPU B. No radio model,
departures, stochastic estimation, command-order transitions, partial commits,
delay cost, horizon or O-RAN interface is implemented here.

## An exact limitation, rather than a new algorithm

When the same new assignment must satisfy every scenario, these constraints
are exactly equivalent to replacing b_s,k with max_s b_s,k separately for each
resource. To prove this, fix any resource k: the new demand does not depend on
s, so satisfying its largest existing load is necessary and sufficient for
all its scenarios. Applying this argument to every resource proves equivalence.
Correlation between possible loads does not improve this static robust
feasible set. A richer name for pending-command uncertainty creates no new
allocation capability under these assumptions.

## Independently implemented comparators

`reference` enumerates Cartesian assignments and checks each world directly.
`envelope_solver` uses a separate recursive search on worst-case residual
capacity. They share the problem data, but neither calls the other or shares
a feasibility helper. Both solve the same small one-step robust problem
exactly; neither is a reproduction of a published algorithm or dynamic MPC.
`greedy` uses the same conservative capacity and ordinary fixed-order first
fit. Beating this deliberately simple ordering does not establish novelty.
The exact reference is the strongest objective comparator for this finite
one-step model, but exhaustive enumeration does not scale.

The first diagnostic offers a flexible request followed by an A-only request.
Joint allocation serves both by placing the flexible request on B; first fit
serves one. This is an ordinary packing/ordering effect. In the second, an
unconfirmed migration could occupy either route; robust admission rejects a
6-unit request on both. An outcome-contingent allocator could make another
choice after receiving new information, but cannot use that future information
at the present epoch.

Two constructed cases and 100 seeded generated instances are executed.
Inputs and exact assignments are retained in results.json. Assertions check
exact/envelope objective equality, exact dominance over greedy and the two
diagnostic outcomes. These are implementation checks and a finite diagnostic
set, not statistical evidence of network performance or independent code review.

## Research decision

Reject static ACK-aware joint robust allocation alone as the proposed novel
contribution. It reduces to conventional reservation plus a packing problem.
Do not start a large RL campaign or infer a publication-ready contribution.
The thesis title and completed PRORL artifacts need not change.

A possible next hypothesis is a sequential decision to wait for information,
probe/reconcile state, or commit a coupled allocation before a deadline.
Information acquisition must have an explicit cost and protocol-grounded
observation model. Before implementation or novelty claims, review closest
full-text work and compare to an independent belief-state or finite-horizon
control reference with exactly the same information and actions. This file
does not claim that hypothesis is new or that it will outperform those methods.
