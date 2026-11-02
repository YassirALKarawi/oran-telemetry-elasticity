# Scientific audit and redesign decision

**Status, 2 November 2026: scientific redesign required before submission.** The existing PDF is a reproducible research draft. Formatting completion and passing software tests do not establish a strong new contribution. This audit is separate from its frozen experiments.

## What was actually completed

840 additional simulations use 20 new seeds, seven stress cases, and six policies. Both the existing weighted scheduler and local earliest-deadline-first (EDF) are evaluated with the existing risk controller, static capacity, and maximum capacity. The protocol was written before executing these runs. No parameter was fitted to their outcomes. An independent single-stage relaxation checks whether radio capacity alone prevents timely completion. All records are in `results.json.gz`, with a convenient `summary.csv` and `verification.json`.

The verifier checks 300 independent maximum bipartite matching instances, 300 independent EDF scheduling instances, all result identities, and 12 fresh simulation replays. These checks passed. They validate this audit implementation, not physical O-RAN fidelity.

## Findings that determine the redesign

| Stress case | Existing controller, weighted: class 0 / class 1 miss (%) | Same controller, EDF: class 0 / class 1 miss (%) | Interpretation |
|---|---:|---:|---|
| Markov load | 0.0032 / 0.6188 | 0.4126 / 0.4708 | EDF redistributes failures, without satisfying both class targets |
| Compound arrivals | 0.8342 / 2.6195 | 1.8884 / 2.1615 | Both local policies fail under the offered load |
| 50-slot activation | 0.2830 / 7.7270 | 2.1141 / 2.7128 | Reactive elasticity fails although static capacity succeeds |

These are descriptive means over 20 seeds. They are not confidence bounds. The class target is 0.1%, and the original reliability qualification requires more than a favorable point estimate.

In the compound-arrival case, an optimistic relaxation gives a pooled unavoidable miss fraction of **0.2602%** across the measured packets. The mean per-trace lower bound is **0.2575%**, positive on seven of 20 traces. The relaxation removes downstream bottlenecks and all outside-cohort interference. The radio capacity is unchanged because the current controller has no radio expansion authority. Thus, even perfect downstream control cannot eliminate these particular overload losses. This does not imply that all observed losses are unavoidable. It also does not establish a stochastic guarantee from 20 traces.

At 50-slot activation, the static (2,0) baseline has zero observed misses in both classes in these runs, at cost 6680. The dynamic weighted controller costs 4493.77 on average and fails the deadline objective. Maximum capacity costs 20040 and also has zero observed misses in this case. The problem is therefore partly the timing and amount of provisioned capacity, not simply insufficient maximum downstream capacity.

EDF is not a new contribution, and this audit does not support replacing the original scheduler and declaring success. Existing pending-command evidence also remains inconclusive. Neither finding will be removed to improve the apparent paper quality.

## Mathematical basis of the capability audit

For a packet p born at b_p with deadline D_p, the original three-stage engine requires radio service in the inclusive interval [b_p, b_p+D_p-3]. Two later slots are necessary for its transport and compute service. Create one available service position for every unit of radio capacity c_0(t). Match each measured-cohort packet to an eligible position. Discard all other traffic and assume unlimited downstream resources.

Let M* be the maximum number of matches and N the offered cohort size. Every feasible completion in the full network induces a valid radio match, so its number of deadline misses is at least N-M*. This is a necessary feasibility bound, not a sufficient network admission rule. Sorting available unit jobs by their deadlines attains maximum cardinality in this interval matching problem: at the first disagreement with an optimal matching, the earliest-deadline available job can replace a later-deadline job, and the displaced job can take the earlier job's later position if needed. Repeating the exchange preserves cardinality. `verify.py` additionally compares the implementation with SciPy's independent bipartite matching solver.

## Research direction to test, not an established contribution

Working direction: **Deadline-Feasible Cross-Domain Orchestration in O-RAN under Delayed Control**.

The useful question is when a delayed orchestrator can make a feasible end-to-end service commitment, and what resource/admission decision is required when it cannot. The old idea of including pending commands in a queue predictor is insufficient as the central claim.

The redesigned decision should coordinate radio allocation, transport capacity, and compute provisioning within explicit physical budgets. It should use local deadline scheduling and a slow resource controller, with a feasibility check before admitting commitments or releasing capacity. Control authority must be explicit: allocating PRBs cannot create radio bandwidth, and changing CPU quotas cannot remedy a radio bottleneck. Reservations may protect deadlines only under stated service lower bounds and bounded actuation assumptions. A violated assumption must be detected and reported.

For a finite packet set, a reference feasibility formulation uses binary admission a_p and binary service assignment x_{p,i,t}. Require exactly one service unit at each stage for every admitted packet, sum_t x_{p,i,t}=a_p. Enforce stage capacity sum_p x_{p,i,t}<=c_i(t), release/deadline windows, and precedence sum_{u<=t} x_{p,i+1,u}<=sum_{u<t} x_{p,i,u}. Capacity c_i(t) must reflect actual activation times of immutable issued commands. A practical online approximation must be compared against this finite-horizon reference on small instances. This formulation is a proposed design specification. It has not been implemented or proved novel by this audit.

Optimize timely delivered offered traffic subject to a common resource budget, then compare resource cost at matched service levels. Report rejected/offered, late-admitted/offered, late-admitted/admitted, and timely-delivered/offered separately. Rejecting difficult traffic must not be counted as serving it reliably. All comparators require the same physical budgets and information access.

Required evidence before a new submission recommendation:

1. Establish the specific technical difference from MAREA, predictive admission/allocation, and delayed-control literature. The presence of two control timescales, MPC, admission, or a command ledger alone is not enough.
2. Validate radio/service and control-latency modeling using measured data or a standards-based platform. Keep trace replay, calibrated simulation, and actual closed-loop deployment clearly distinguished.
3. Reproduce an external algorithm in its original documented setting before adapting it. Preserve exact equations, code provenance, parameter tuning budgets, and an explicit adaptation table.
4. Compare the full design with static provisioning, local EDF, prediction-only control, and a finite-horizon optimization reference. Use ablations that isolate each claimed component at matched capacity budgets.
5. Freeze training/calibration choices before a new independent evaluation. Include infeasible cases, distribution shift, control jitter, runtime, scalability, and uncertainty. These audit seeds are now development evidence and cannot be reused as untouched confirmation.

These are research deliverables, not formatting edits. No new manuscript is labeled submission-ready on the basis of this audit.

## Sources inspected and remaining evidence gaps

- [MAREA, author full text](https://arxiv.org/html/2503.08599v2), DOI 10.1109/TCOMM.2025.3552296: already combines near-real-time resource decisions with a faster anomaly response and a martingale-based delay model. A generic two-timescale proposal would overlap substantially.
- [Predictive slice admission and VNF allocation, IFIP Networking 2024](https://dl.ifip.org/db/conf/networking/networking2024/1570998370.pdf): joint admission, placement, and predictive control already exist. Adding these terms to the title does not establish novelty.
- [MetBS official implementation](https://github.com/MikeKalnt/MetBS), inspected at commit `fc65e424dd8889900aadee36f2059d009a773e4f`, notebook blob `53c2a1f45c5e753624b2ad1de40fe324a716d56e`. The public notebook's utility and power functions are explicitly dummy random functions. It is useful algorithm source, but does not by itself reproduce the paper's measured power/throughput experiment. The inspected repository tree contains only the README and notebook. No external superiority result has been claimed from it.
- [Open RAN commercial traffic twinning dataset](https://openrangym.com/datasets/open-ran-commercial-traffic-twinning-dataset): a candidate public source with timestamped radio and application measurements from Colosseum experiments driven by commercial traffic traces. Its [repository](https://github.com/wineslab/open-ran-commercial-traffic-twinning-dataset) identifies metrics and log archives. These data have been located, not downloaded or validated in this audit. Static allocation traces cannot simply be stitched together and presented as the result of a newly deployed dynamic controller. Transport/compute timing and command transition effects require their own evidence.

## Reproduce

Python 3.10+, NumPy, and SciPy are required. From the repository root:

```bash
python research_audit/audit.py
python research_audit/verify.py
```

The first command generates `research_audit/results.json` from all 840 executions. The second can read that file or the distributed gzip copy. Existing manuscript data and source are unchanged.
