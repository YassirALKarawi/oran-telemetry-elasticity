# Sensitivity to the training budget in the tandem simulator

The protocol was frozen before the new tests at commit 3de8655e54ee8a357f8edc7777f0b54a5388c699. Each seed followed one training trajectory. All budgets kept the same model, reward, exploration schedule, environment and action set. Longer training also exposed the controller to more training traces from the same scenario generator. Each budget had two validation candidates and used the same three validation traces. The five selected short-budget models matched the previously archived weights tensor for tensor.

## Held-out results

Costs, resource use, and per-trace p99 delays are arithmetic means. Lower cost is preferable under the prespecified backlog, capacity and switching penalty. Misses and mature-packet denominators are pooled across each row; the learned policies repeat the same arrivals under five independently seeded models.

| Scenario | Controller / training decisions | Cost | Extra unit-slots | Mean p99 (slots) | Misses / eligible |
|---|---|---:|---:|---:|---:|
| nominal | Thesis | 125.57 | 35.0 | 4.00 | 0 / 5095 |
| nominal | Greedy | 157.95 | 192.0 | 4.20 | 0 / 5095 |
| nominal | Adapted DDQN / 1,296 | 329.33 | 1062.4 | 4.04 | 0 / 25475 |
| nominal | Adapted DDQN / 3,888 | 309.67 | 956.2 | 4.04 | 0 / 25475 |
| nominal | Adapted DDQN / 11,664 | 287.40 | 838.4 | 4.16 | 0 / 25475 |
| bursty_transport | Thesis | 664.10 | 695.0 | 25.20 | 0 / 6395 |
| bursty_transport | Greedy | 637.46 | 656.0 | 25.40 | 90 / 6395 |
| bursty_transport | Adapted DDQN / 1,296 | 894.71 | 1084.2 | 35.52 | 1383 / 31975 |
| bursty_transport | Adapted DDQN / 3,888 | 748.28 | 1084.0 | 31.12 | 1699 / 31975 |
| bursty_transport | Adapted DDQN / 11,664 | 796.16 | 1138.8 | 32.08 | 1390 / 31975 |
| bursty_compute | Thesis | 722.46 | 673.0 | 25.80 | 0 / 6353 |
| bursty_compute | Greedy | 672.61 | 653.0 | 24.20 | 69 / 6353 |
| bursty_compute | Adapted DDQN / 1,296 | 1069.72 | 1098.4 | 40.64 | 2883 / 31765 |
| bursty_compute | Adapted DDQN / 3,888 | 1426.74 | 1034.0 | 60.52 | 8447 / 31765 |
| bursty_compute | Adapted DDQN / 11,664 | 889.64 | 1109.2 | 36.56 | 2987 / 31765 |

## Paired cost differences relative to 1,296 decisions

| Scenario | Budget | Mean difference | Seed-level means below short budget |
|---|---:|---:|---:|
| nominal | 3,888 | -19.66 | 4 / 5 |
| nominal | 11,664 | -41.93 | 3 / 5 |
| bursty_transport | 3,888 | -146.43 | 4 / 5 |
| bursty_transport | 11,664 | -98.55 | 3 / 5 |
| bursty_compute | 3,888 | +357.02 | 1 / 5 |
| bursty_compute | 11,664 | -180.08 | 3 / 5 |

## Interpretation and reproducibility

There are five training seeds and five new traffic traces per scenario. Models at different budgets on the same training seed are paired. Aggregate comparisons are descriptive. The published native PRORL transfer-task benchmark uses a different action space and reward. These tests measure a PRORL-derived Double DQN controller in a synthetic tandem queue. End-to-end SDN/RIC actuation remains to be verified.

The three scenario JSON files contain every test result and trace digest. Each seed file contains validation costs for all candidate episodes and the three selected model states with SHA-256 digests. From the repository root use the pinned baseline_prorl interpreter to run common_environment/adapted/budget_study/study.py with replay to verify all 255 policy–trace outcomes. The train and test phases regenerate the weights and results, respectively. Run summarize.py to rebuild these tables.
