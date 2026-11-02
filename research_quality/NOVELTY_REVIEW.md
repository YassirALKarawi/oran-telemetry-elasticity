# Scientific positioning review — 2 November 2026

## Decision

The current joint_allocation package is validated software infrastructure, not an established novel contribution. The original thesis title can remain. Do not submit its generic routing/placement model as a new O-RAN contribution on the basis of the existing development experiments.

## Closest work identified

| Source | Relevant existing contribution | Consequence for this project |
|---|---|---|
| [On flexible association and placement in disaggregated RAN designs, 2025](https://www.sciencedirect.com/science/article/abs/pii/S0140366425001239) | Joint admission/association/placement, exact optimization and faster approaches, including bottleneck analysis | Joint placement, admission and comparing exact versus greedy are not sufficient novelty |
| [Federated Learning Assisted Deep Q-Learning for Joint Task Offloading and Fronthaul Segment Routing in Open RAN](https://doi.org/10.1109/TNSM.2023.3245544), IEEE TNSM 20(3), 3261–3273, 2023 | Joint offloading, transport routing and edge processing with a delay objective | Joint routing and processing alone is established prior work |
| [An Optimal Framework for Integrating O-RAN and MEC via Pooled DU/CU Deployment](https://doi.org/10.1109/TGCN.2026.3690004), 2026 | Joint placement/resource optimization with processing and transport delays | A generic MILP is infrastructure, not automatically a paper contribution |
| [Multi-tier O-RAN Optimization for 5G and beyond networks](https://www.sciencedirect.com/science/article/pii/S1389128626004081), 2026 | Joint compute placement and optical xHaul allocation with an exact model and scalable heuristic | A cross-domain title and an exact/heuristic pair are not sufficient distinctions |

This is an overlap screen based on retrieved publisher/institutional descriptions, abstracts and available introductory text. It is not a completed full-text systematic review or a proof that every possible extension is already studied. Direct full-text retrieval of the first publisher page returned 403. No external algorithm has been faithfully reproduced yet, and none is labeled as such in the benchmark.

## Evidence required before manuscript finalization

1. A specific claim that differs from the closest work, with full-text equation and assumption comparison.
2. Reproduction of a suitable external baseline before adaptation, with an explicit mapping and equal information/tuning budgets.
3. Independent topology and workload evaluation after freezing the algorithm. Preserve infeasible and unfavorable cases.
4. Matched offered traffic, admitted request identities where applicable, service targets and resource budgets. Report failures and rejections separately.
5. Runtime/scaling and exact optimality gaps on solvable cases, with uncertainty across independent instances.
6. An explicit account of radio, transport and processing abstractions. Generic graph routing is not deployed SDN or an O-RAN protocol implementation.
7. Numerical, reference, figure and manuscript consistency checks before declaring submission readiness.

No benchmark result, publication acceptance or scientific novelty is promised in advance. Three manuscripts require three independent contributions, not cosmetic partitions of these experiments. The research gate remains open until the missing evidence is produced.
