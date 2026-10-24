# O-RAN telemetry pilot

Student: Fatima Subhi Khaleel

Working paper: Joint Telemetry Refresh and Resource Allocation for Delay-Constrained SDN-Orchestrated O-RAN

## Status and scope

This package is an executable **abstract feasibility pilot**, not a complete O-RAN simulator, final publication evidence, a validated NR model, or a real network experiment. It has no E2, O1, O2 or OpenFlow implementation. No novelty or performance superiority is asserted.

Python 3.10+ is sufficient. No third-party dependencies.

```
python simulate.py --test
python simulate.py --seeds 20 --steps 3000 --output results.json
```

## Model

Two service classes traverse FIFO radio, transport and compute queues. Each packet consumes one abstract service unit in each stage. One slot represents 20 ms. Capacity values, arrivals and deadlines are deliberately synthetic and are not calibrated to a deployment. Per-stage capacities are 5 packets/slot before variations. Service deadlines are 15 and 40 slots. These are not URLLC targets.

Exogenous arrivals and capacities are generated before each run and shared across policies. Nominal traffic is independent Poisson with means 0.9 and 2.1 packets/slot. Bursts use means 1.8 and 3.8. Stress scenarios reduce transport or compute capacity to 3 packets/slot during a recurring congestion interval. All queue state is available to the simulation engine, but the supervisory policy only reads delivered reports.

One equally-sized resource report is requested every five slots. Reports arrive three slots later or are lost with probability 0.05. A request snapshots that stage's queues, recent ingress rates and available capacity. All three stages have the same nominal report size. Policies therefore share the request and delivered-report budgets under the same seed. Transport contention caused by telemetry itself is NOT modeled yet.

Three policies choose the reported stage: cyclic periodic, oldest delivered measurement, and a decision-impact heuristic using observed pressure and age. The latter is a hypothesis, not an optimized value-of-information solution. Allocation uses integer weighted shares based on estimated queues and service deadline. The local scheduler enforces actual stage capacity, without exposing it to the supervisory controller. Unused reserved shares are not borrowed by the other class. This deliberate simplification needs a work-conserving scheduler sensitivity test.

Reports requested now cannot affect allocation until delivered. Downstream-first processing prevents packets crossing multiple stages in a single slot. Runtime packet-conservation assertions are enabled.

## Interpretation

Violations count late completed packets AND already-overdue unfinished packets. Remaining unfinished packets younger than their deadline are censored at the horizon. Completed-packet percentiles are explicitly completion-conditioned and must not be interpreted alone as overall service quality. Report pending/loss counts and unfinished packets are preserved in results.

Confidence intervals in the JSON summary are descriptive normal approximations across 20 independent seeds. They are not paired significance tests. The simulation horizon includes startup and has no warmup removal. Policy choice, heuristic weights, horizon and scenario designs are not tuned against reported results.

## Tests

Six automated checks cover resource-budget accounting, empty arrivals, minimum tandem delay, equal telemetry budgets and identical traces, deterministic reproducibility, and no delivery before the specified report delay. Passing them does not establish physical fidelity or a QoS proof.

## Next research gates

1. Systematic closest-work comparison before claiming novelty.
2. Calibrate stage service demands, arrivals, deadlines and measurement errors from identifiable sources.
3. Replace heuristic uncertainty with validated predictive intervals.
4. Derive joint update/allocation optimization and compare against an exact small-instance solver.
5. Model telemetry load on transport and compare work-conserving schedulers.
6. Account for horizon censoring, warmup, seed uncertainty and paired statistical tests.
7. Perform delay/loss/load/scale sweeps and component ablations.
8. Validate an implementable control split among RIC, SDN and cloud orchestration.

## Verified nearby literature

- MAREA: A Delay-Aware Multi-time-Scale Radio Resource Orchestrator for 6G O-RAN. IEEE Transactions on Communications. https://doi.org/10.1109/TCOMM.2025.3552296 . Author version: https://arxiv.org/abs/2503.08599 . Its radio-only evaluation is not directly comparable to this tandem abstraction.
- Adaptive Resource Allocation for Virtualized Base Stations in O-RAN With Online Learning. IEEE Transactions on Communications 73(3), 1787–1800, 2025. https://doi.org/10.1109/TCOMM.2024.3461569 . This is a relevant performance/energy and online-learning comparator, not a baseline implemented here.

The earlier proposed paper titles remain candidate topics. This pilot does not replace or certify any previously created manuscript or simulation.

## Recorded pilot run (2026-10-06)

20 seeds, 3,000 slots per run, three scenarios, three policies: 180 runs.
Six automated tests passed. Raw per-seed outputs are in results.json.

Sensitive-class observed deadline violation rates (percent of generated packets):

| Scenario | Periodic | Oldest | Impact heuristic |
|---|---:|---:|---:|
| Nominal | 30.86% | 28.06% | 26.59% |
| Bursty transport | 68.27% | 67.31% | 67.64% |
| Bursty compute | 65.80% | 65.20% | 64.65% |

The impact heuristic has a lower sample mean than periodic allocation in these
three scenarios, but does not beat oldest-first in the transport stress scenario.
It also has higher mean total backlog than oldest-first in every scenario.
There is therefore no evidence here of universal superiority or dependable QoS.
The high violation rates and backlog expose limitations of the allocation and
prediction heuristics, along with overloaded stress intervals. This is a useful
negative diagnostic, not a publication-ready gain. No significance is claimed.

Next engineering priority is a work-conserving deadline-aware local scheduler,
followed by a calibrated uncertainty estimator and an explicitly optimized
update/allocation decision. New variants should be evaluated on held-out seeds
and stress settings, keeping this pilot as an unchanged baseline.
