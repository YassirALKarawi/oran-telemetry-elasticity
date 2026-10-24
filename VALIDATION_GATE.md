# External-validation and publication gate

## Completed within the abstract model

Current revision: 22 October 2026, `paper_reliability/Manuscript.pdf`.

- Paired exogenous traces, separated calibration and evaluation seeds.
- Fair telemetry request budgets and explicitly delayed command activation.
- Arrival-cohort deadline accounting including unfinished packets.
- Bounded capacity additions and incremental resource/switching cost.
- Stronger fixed-capacity selection independent of evaluation outcomes.
- Mathematical model, finite-grid proof, work-conservation and capacity-cut proofs.
- Independent packet replay, independent optimizer enumeration, regression tests.
- Component-isolation experiments and action-delay sensitivity under a locked protocol.
- Common 0.1% classwise risk screen, 336 calibration and 840 held-out executions.
- Markov/compound workload shifts, degraded reports and variable command delays.
- Transparent HPA-inspired and DPP-inspired adaptations, with failed calibration disclosed.
- 43-reference review and complete result-driven manuscript, with resolved PDF references.

## Not completed, and why it matters

1. **Physical model calibration.** A service unit is not a measured radio resource,
   transport byte or CPU cycle. One cannot convert the existing savings to energy,
   money, spectrum efficiency or real O-RAN SLA improvements.
2. **External validation.** No trace or independently calibrated network simulator
   has reproduced these results. Independent replay only verifies internal logic.
3. **Closest published baselines.** No MAREA, BSvBS/MetBS or other closest algorithm
   has been faithfully reimplemented and evaluated under compatible assumptions.
4. **Novelty.** Finite-grid optimality and queue conservation are correctness facts,
   not substantial research novelty. A new guarantee or strongly evidenced insight
   must be identified before a Transactions submission.
5. **Statistical strength.** Six calibration seeds and twenty held-out seeds per
   setting do not certify rare-event reliability. All-zero percentile intervals
   are descriptive, and no simultaneous coverage across screens is claimed.
6. **Scope of three papers.** There are not three independent completed studies.
   Reusing these outputs under three titles would not establish distinct contributions.

## Minimum input for a defensible physical study

An external validation extension must adopt a documented system-level simulation
or measured-system route and specify the deployment scenario before claiming
physical results. This requirement does not depend on the student supplying
files. Hardware is not mandatory for every theoretical paper, but internal
software checks alone do not validate a physical model.

The calibration record must identify:

| Domain | Required evidence |
|---|---|
| Radio | Carrier, bandwidth, numerology, topology, users, channel model, antenna setup, scheduler, MCS and retransmission behavior, simulator version/commit |
| Transport | Link rates in bit/s, packet sizes, propagation, buffers, routing and exact SDN actions/control delay |
| Compute | Workload definition, cycles or service-time distribution per job, processor capacity, scaling delay and profiling source |
| Workload | Per-class arrival process/trace provenance, payload size, deadline and allowable miss target |
| Control | Report fields and sampling, delay/loss distributions, command queue/supersession rules, actual resource pool limits |
| Validation | Independent reference outputs and a tolerance fixed before comparison, calibration/evaluation split, all discrepancies reported |

## Proposed external-validation procedure, not executed results

1. Pin simulator and dependency versions. Reproduce a documented calibration case
   with its original topology, channels and evaluation metrics.
2. Archive raw outputs and reference curves. Set metric-specific tolerances before
   comparing, based on published calibration ranges rather than an arbitrary score.
3. Add the control mechanism without changing the calibrated data-plane defaults.
   Keep radio, transport and compute units explicit, with per-packet work demands.
4. Measure telemetry/actuation overhead and distinguish monitoring from decisions.
5. Reproduce the closest compatible published policy before extending it. If a
   baseline cannot be mapped fairly, document why and do not compare incompatible
   reported percentages.
6. Freeze a new evaluation design, seeds, topology/load sweep, parameter sensitivity
   and primary endpoints. Reevaluate all policies under the same information budget.
7. Produce raw logs, paired uncertainty estimates, failure cases and scale/runtime
   measurements. Only then revise abstract, novelty claims and conclusions.

## Three-paper separation, conditional on later evidence

- Paper A: telemetry selection and capacity elasticity. Needs novelty beyond the
  current surrogate plus a validated model and closest-work baselines.
- Paper B: asynchronous command safety and pending-action-aware control. Needs a
  new controller and a safety/feasibility result, not merely the lag sweep here.
- Paper C: fault recovery and reconfiguration. Needs explicit failures, recovery
  actions, recovery-time constraints and separate experiments. None are simulated
  by the current burst cases.

The approved thesis title is retained. Quantum methods are not added by name
without a demonstrated problem-specific need and a fair classical comparison.
