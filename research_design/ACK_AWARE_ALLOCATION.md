# Candidate research design: acknowledgement-aware joint transport and processing allocation

Date: 3 November 2026. Status: focused initial literature audit and executable-study specification; novelty NOT established. This document supersedes the informal suggestion that merely adding telemetry delay and SDN action cost to PRORL would constitute a contribution. The thesis title remains Optimal Resource Allocation in ORAN with SDN-Managed Orchestration.

## Evidence and scope

The completed PRORL experiment remains an immutable external-baseline artifact: 89,400 loop steps, one training seed (10), three evaluation seeds (1000,1100,1200), synthetic four-node constant-load configuration. Its results do not evaluate the candidate below. See ../prorl_reproduction/COMPLETED_RUN.md.

The current repository already models delayed telemetry and actuation, projects pending commands, and contains a joint routing/processing allocator with an exact reference. Its README reports that all seven intervals from the 140-run pending-command diagnostic include zero. Therefore pending-command bookkeeping alone has not demonstrated an incremental benefit in the existing study. The previous 840-run audit also reports long-delay failures. Those negative findings must remain visible.

The initial source search found:
- PRORL, IEEE TNSM (2024), DOI 10.1109/TNSM.2024.3373606: proactive resource allocation with demand satisfaction, utilization and allocation-cost tradeoffs. Source: https://discovery.ucl.ac.uk/id/eprint/10189737/
- ORANUS, accepted INFOCOM 2024: stochastic-network-calculus resource allocation and multiple control timescales. Source: https://arxiv.org/abs/2401.03812
- Delay-sensitive resource allocation for IoT systems in 5G O-RAN networks (2024): publisher abstract describes hierarchical DDQN with SDN and a real testbed. Source: https://www.sciencedirect.com/science/article/pii/S2542660524000738
- Reinforcement Learning with Random Delays: observation/action delays and delay-correcting learning are established topics. Source: https://arxiv.org/abs/2010.02966
- Revisiting State Augmentation methods for Reinforcement Learning with Stochastic Delays: augmented-state delayed-MDP formulations already exist. Source: https://arxiv.org/abs/2108.07555
- Reducing Age-of-Information tails with bridge guarding during delayed reconfiguration in semi-persistent wireless scheduling (publisher search abstract, 2026): protecting command-to-activation intervals is also an existing direction. Source: https://www.sciencedirect.com/science/article/pii/S1389128626007036
- Incentives and Evidence in Learned Service Orchestration (2026 preprint): comparator collapse and artifact choices can distort conclusions about delayed/noisy telemetry. Source: https://arxiv.org/abs/2606.16555

Review depth: repository README and joint_allocation/README were read; literature evidence above is abstract/repository-level screening, not a completed full-text comparison. Publisher full-text access returned 403 for the two ScienceDirect items. Search coverage is not an exhaustive systematic review or patent search. No claim that existing papers omit the proposed combination is justified yet.

## Candidate scientific question

When telemetry and execution acknowledgements are delayed, does explicitly reserving capacity for issued-but-unconfirmed commands improve joint transport-route and processing-destination admission decisions, relative to equally informed prediction and robust-control baselines?

The target mechanism is resource commitment uncertainty: an old report may show free capacity while previously issued commands can still consume it. Ordinary traffic prediction, an age feature or a switching penalty does not by itself define how this commitment is represented. Whether existing work already solves the same problem remains a full-text review gate.

Working title, not a final paper title:
Acknowledgement-Aware Joint Transport and Processing Allocation under Delayed Telemetry and Actuation.

## State, events and information boundary

Build on joint_allocation, keeping its exact small-instance comparator. At each decision epoch the controller receives timestamped reports and execution acknowledgements. Its information consists only of reports delivered by that epoch, issued commands, locally known sequence identifiers, and acknowledgements received.

Each request specifies bandwidth b_i, processing demand c_i, a route/destination alternative set, arrival and departure, and a service-delay budget. Each command has issue time, target resource configuration, resource deltas, and status (queued locally, issued/unconfirmed, acknowledged applied, or acknowledged failed). The simulator stores actual execution time privately; it is never an input to the controller.

Maintain separately:
1. Last confirmed resource state.
2. Capacity that issued commands could still consume.
3. Requests served and actually active at each instant.
4. Controller-side queued proposals that have not been transmitted.

Releasing an unconfirmed reservation solely because of timeout is prohibited unless the modeled protocol provides a validated failure/expiry rule. A missing acknowledgement is not evidence that a command failed. Model ordered per-resource application first; extend to reordering only with explicit device sequence semantics. Do not assume standard E2 supports arbitrary cancellation, transactional route/compute updates, or instantaneous rollback.

Distinguish report age, command execution delay and acknowledgement delay. These are three separate variables. Physical units must come from measured traces or explicitly labeled synthetic slot assumptions; none of the existing abstract costs should be relabeled as energy or actual protocol latency.

## Two algorithm specifications

Algorithm 1 — Commitment-state reconstruction:
- Consume only delivered reports/acknowledgements.
- Reconcile report timestamps with the issued-command ledger; avoid counting an acknowledged change twice.
- For every link and processing node, calculate a conservative range of possible committed load from unresolved commands and known application-order constraints.
- Preserve uncertain commitments until confirmed, superseded under modeled semantics, or reconciled by a sufficiently fresh report.
- Output estimated load, commitment bounds, report ages and a list of controller-side proposals eligible for replacement.

This is an operational estimator, not a new theorem or calibrated uncertainty guarantee.

Algorithm 2 — Bounded-horizon joint admission and allocation:
- Enumerate or generate complete route/destination alternatives.
- Select admit/defer/reject and locally queued proposals using the same request utility and hard capacity constraints across all methods.
- Enforce link and processing capacity for every commitment realization represented by Algorithm 1; use a small exact robust mixed-integer formulation as reference.
- Optimize a declared objective: unmet-request penalty + reserved-capacity cost + command-transmission/change cost. Freeze weights using development data.
- Retain the last feasible confirmed allocation when no feasible proposal is available; report denied/deferred service rather than hiding infeasibility.
- Derive a bounded-candidate approximation for scale only after the exact formulation and simulator agree.

Joint routing/placement, robust optimization and state augmentation are known ingredients. A combination is not automatically a contribution. The candidate must yield a technically distinct formulation or tractable rule with demonstrated mechanism-level value.

## Falsifiable experiments

Gate A — closest-work review: inspect full texts for command ledgers, acknowledgement uncertainty, capacity reservation, joint routing/processing, and protocol assumptions. Record exact page/section evidence and use unknown when unverified. Redesign or stop the novelty claim if the same mechanism exists.

Gate B — deterministic counterexample: construct a small case where stale free-capacity reports and two in-flight allocations cause an avoidable conflict. Compare no-ledger prediction, ordinary action-history augmentation and commitment bounds. Zero-delay and immediate-acknowledgement cases must collapse to the non-delayed allocation problem. This is a correctness/mechanism demonstration, not evidence of broad performance.

Gate C — randomized simulation: include low/high load, correlated bursts, link/compute bottlenecks, varied observation/execution/acknowledgement delay, loss with specified recovery, and 4/8/16/32-node topologies. Use held-out topology/traffic/delay combinations.

Methods:
- Existing exact joint allocator on small instances, with an explicit perfect-information oracle label where applicable.
- Joint greedy with the same information and command interface.
- PRORL adaptation with age/action-history state and identical capacity/command semantics; budget retraining fairly. Original PRORL metrics cannot be directly compared with a different transport/compute simulator.
- Robust/model-predictive allocation with the same demand predictor and commitment information.
- Candidate exact and approximate variants.
- Ablations removing only acknowledgement uncertainty handling, pending commitments, or joint route/processing coupling.

Use at least five independent training seeds for learned methods. Use at least twenty held-out environment seeds, paired exogenous traffic/failure events across methods, and report training-seed and environment-seed variability separately. Tune all methods on development data; freeze objectives, selection rules and primary contrasts before held-out evaluation.

Primary outcomes: requested-service violation rate and realized capacity conflicts under equal offered load. Secondary outcomes: admissions/defer/reject counts, completion-conditioned delay plus unfinished/deadline accounting, reserved resources, command count/bytes, allocation churn, and wall-clock solver cost. Report cost comparisons at matched service levels or on a service/cost frontier.

Zero observed conflicts do not prove a universal guarantee. No safety/SLA theorem should be claimed without explicit bounded-delay/order assumptions and a proof. Confidence intervals must use independent experimental units, not individual correlated packets as independent samples.

Gate D — success or stop decision: require a practically meaningful benefit over the strongest matched comparator with uncertainty reported, without concealing resource/service tradeoffs. If gains disappear with equal information, budgets and scheduler semantics, reject the mechanism claim and redirect effort.

## Authorized next implementation

First implement the event model and deterministic counterexample with conservation and causal-information checks. Do not launch a large training campaign before Gates A/B establish a defensible target. Preserve the completed PRORL baseline and historical negative diagnostics. A new algorithm, a full standards implementation and a submission-ready manuscript are not delivered by this design document.
