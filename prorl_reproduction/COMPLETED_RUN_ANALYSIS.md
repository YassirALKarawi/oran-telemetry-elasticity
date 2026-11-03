# Analysis of the completed PRORL run

4 November 2026. Analysis of existing outputs; no new training/evaluation was executed.

## Integrity and experiment scope

The available recovered_full.json and recovered_full.pt SHA-256 values were recomputed and matched completion_audit.json. The completion report in the repository was also read. The saved run completed 89,400 loop steps including bootstrap, with training seed 10, validation seed 100 and evaluation seeds 1000, 1100, 1200. Each evaluation had 168 steps. Raw paired values and hashes of each baseline input are saved in completed_run_analysis.json.

## Paired utility values

| Evaluation seed | PRORL | Greedy | Heuristic | PRORL minus Greedy |
|---|---:|---:|---:|---:|
| 1000 | 137.740005 | 117.689995 | 118.619995 | 20.050011 |
| 1100 | 136.399994 | 117.279999 | 116.599998 | 19.119995 |
| 1200 | 135.860016 | 117.440002 | 117.970001 | 18.420013 |

Mean paired utility difference is +19.196673 versus Greedy and +18.936673 versus Heuristic. These are observed differences in the upstream reward, not physical service units or proven general advantages.

## Tradeoffs from the existing matched summary

| Metric | PRORL | Greedy | Heuristic |
|---|---:|---:|---:|
| Utility reward | 136.666672 | 117.470001 | 117.730003 |
| Remaining gap (upstream signed metric) | -93.333333 | -248.333333 | -248.666667 |
| Surplus | 320.000000 | 151.333333 | 148.000000 |
| Cost (upstream metric) | 18.666667 | 233.000000 | 231.000000 |
| Hours satisfied | 150.333333 | 114.000000 | 112.333333 |
| Resource utilization | 0.904546 | 0.950254 | 0.951313 |

The learned policy improves utility and some other recorded metrics in this particular experiment while increasing surplus and reducing utilization. Reward optimization can favor such tradeoffs; their mechanism requires tracing the upstream metric definitions and action histories. This analysis does not assign a physical interpretation to cost, prove causality, or infer uniform dominance. Hours satisfied is an upstream synthetic counter, not a measured duration of live service.

## What can be reused

The selected saved model can support additional held-out evaluations if its source, dependency versions, observation/action schema and resource configuration remain compatible. New traffic within that schema can test generalization without automatically retraining. A changed transport/CPU action space or changed observation representation requires an explicit adapter/model compatibility check; do not silently load this checkpoint into the new environment.

PRORL remains a published comparator. The later ACK diagnostics are separate abstract experiments and cannot be combined numerically with its utility scores.

## Remaining evidence

A complete paper-setting audit, independent training seeds and held-out workload conditions are needed. Three evaluation seeds from one trained checkpoint do not measure training variability. No population confidence interval or significance test is claimed here.

Before the next campaign, freeze environment/reward/resource initialization, include ordinary strong allocators with matched information and actions, predeclare held-out traffic and report all tradeoff metrics. A practical initial design is five independent training seeds followed by paired held-out evaluation workloads; five is a starting budget, not a guarantee of statistical power. Choose further replication from measured variability and the target precision.

## Decision

Reuse and retain this completed baseline. Its value is a verified starting point and matched synthetic comparator. The next scientifically useful step is the configuration/metric audit and a predeclared evaluation design, while live SDN validation remains separately blocked. No scientific novelty, manuscript readiness or journal submission follows from training completion.
