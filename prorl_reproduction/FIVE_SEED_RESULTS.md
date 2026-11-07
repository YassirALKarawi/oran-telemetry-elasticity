# Five independent PRORL training seeds

Each run completed 86,400 training iterations plus 3,000 bootstrap decisions. Each saved model and numeric results file passed the finite-value checks. The configured training seeds were 10, 20, 30, 40 and 50. All five exported training configurations matched after replacing the training seed. Model selection used validation seed 100 and the validation utility metric.

## Initial evaluation

Each validation-selected model ran for 168 steps on each of evaluation seeds 1000, 1100 and 1200. The last column gives the mean episode utility for those three seeds.

| Training seed | Decisions | Finite model tensors | Best validation iteration | Initial utility |
|---:|---:|---:|---:|---:|
| 10 | 89,400 | 146 | 72 | 136.667 |
| 20 | 89,400 | 146 | 69 | 136.573 |
| 30 | 89,400 | 146 | 67 | 132.717 |
| 40 | 89,400 | 146 | 89 | 137.040 |
| 50 | 89,400 | 146 | 81 | 136.867 |

## Matched frozen-model evaluation

Each cell for PRORL averages ten 168-step episodes on the same evaluation seeds 2000–2009. Initialization RNG was reset to 10. The trained policy was frozen across all three demand amplitudes. Greedy and Heuristic reproduced the same episode utilities across all five evaluations for each demand. The sample standard deviation measures variation across five trained policies on these fixed traces.

| Demand | Seed 10 | Seed 20 | Seed 30 | Seed 40 | Seed 50 | Mean | Sample SD | Greedy | Heuristic |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 60 | 106.000 | 105.402 | 104.504 | 104.848 | 105.462 | 105.243 | 0.581 | 121.676 | 121.677 |
| 80 | 137.120 | 137.768 | 135.896 | 137.736 | 137.594 | 137.223 | 0.786 | 116.670 | 117.009 |
| 100 | 108.964 | 111.512 | 109.306 | 111.328 | 111.142 | 110.450 | 1.214 | 110.844 | 111.800 |

| Demand | Mean PRORL − Greedy | Seeds above Greedy | Mean PRORL − Heuristic | Seeds above Heuristic |
|---:|---:|---:|---:|---:|
| 60 | -16.433 | 0/5 | -16.434 | 0/5 |
| 80 | +20.553 | 5/5 | +20.214 | 5/5 |
| 100 | -0.394 | 3/5 | -1.350 | 0/5 |

## Resource allocation outcomes

PRORL values average the five training-seed summaries. Each baseline value is taken once on the same ten evaluation seeds. The metric names and units follow the synthetic simulator.

| Demand | Policy | Remaining gap | Surplus | Cost | Hours satisfied | Resource utilization |
|---:|---|---:|---:|---:|---:|---:|
| 60 | prorl | -48.940 | 927.100 | 25.160 | 157.500 | 0.722 |
| 60 | greedy | -207.100 | 160.700 | 236.600 | 119.000 | 0.933 |
| 60 | heuristic | -206.000 | 162.300 | 237.300 | 118.800 | 0.932 |
| 80 | prorl | -96.260 | 304.500 | 19.120 | 150.680 | 0.909 |
| 80 | greedy | -251.700 | 155.600 | 235.800 | 115.200 | 0.949 |
| 80 | heuristic | -247.600 | 157.900 | 236.100 | 116.400 | 0.949 |
| 100 | prorl | -468.560 | 2.840 | 23.040 | 8.460 | 0.999 |
| 100 | greedy | -466.200 | 2.700 | 21.000 | 8.700 | 0.999 |
| 100 | heuristic | -461.000 | 0.500 | 17.000 | 8.900 | 1.000 |

## Scope and next experiment

The comparison covers synthetic bandwidth allocation in the upstream constant-load emulator. Demand 60 exposes a reversal relative to the training demand of 80. The paired episodes within a trained policy share weights. Treat the five independently trained policies as the replication units. The matched demand-shift tests are now disclosed diagnostics.

The thesis policy still requires a common environment with identical observations, action feasibility, resource budgets, traffic traces, telemetry and actuation delays for every comparator. A method revised after inspecting these loads requires a fresh frozen test set. The study has yet to demonstrate end-to-end SDN/RIC actuation or establish methodological novelty.

## Reproducing the audit

Verify the archive entries with `sha256sum -c SHA256SUMS`. To rerun the audit, extract into `prorl_reproduction/` alongside a compatible `baseline_prorl/` checkout. Use the revision in the protocol, apply `baseline_compatibility.patch`, and use the pinned environment in `environment.txt`. Run `baseline_prorl/.venv/bin/python prorl_reproduction/verify_five_seed_results.py` from the project root. All five model files, full run metrics and exported configurations, and per-episode evaluation files are included. The seed-50 checkpoint at 89,000 is the last periodic recovery point. The final JSON and model record completion at 89,400.

[Common-environment requirements](COMMON_ENVIRONMENT_GATE.md) · [Protocol](FIVE_SEED_PROTOCOL.json) · [Machine-readable results](FIVE_SEED_RESULTS.json)

## Archived models and raw results

[Download the verified five-seed experiment bundle](https://chatgpt.com/library?file_id=libfile_f68a645f19b08191ade4437e39a9570e&account_id=personal) (owner account access). SHA-256 of the ZIP is `077539d2d2a251f8ea86481cff53413dc8658108446556105ce9599c816d747c`. The internal SHA256SUMS covers 156 files.
