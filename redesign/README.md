# Executed foundation for the research redesign

This directory contains a verified finite-horizon optimization reference and a descriptive inspection of experimental radio data. It is not a finished new paper, an implemented online controller, or a demonstration of a novel algorithm.

## Executable model

`reference.py` jointly selects admitted packets, their service slots across all stages, and optional constant transport/compute expansion after a specified actuation delay. The objectives are lexicographic: maximize timely served offered packets, then minimize added capacity-unit slots. Rejected packets remain in the offered-load denominator. Existing mandatory commitments cannot be rejected. Radio capacity is an explicit constraint and cannot be expanded by this interface.

An explicit schedule certificate is checked independently after solving. The reference knows all packet releases and capacities within the finite instance. It therefore provides an offline capability benchmark and must not be presented as an online policy with causal observations. The mathematical formulation appears in `../research_audit/README.md`.

## Completed experiments

Four unit tests pass, including 60 random small instances compared with exhaustive independent enumeration. Tests also cover mandatory infeasibility, late actuation, and avoiding unnecessary expansion. A separate synthetic benchmark solves 120 instances: 20 seeds, 24 offered packets per seed, and six activation delays. Every solve must attain optimal solver status. Admission cannot increase when activation is delayed on the same instance, and this relation is checked during execution.

| Activation delay (slots) | Timely served / offered | Mean extra capacity-unit slots |
|---:|---:|---:|
| 0 | 98.9583% | 40.50 |
| 1 | 98.9583% | 38.25 |
| 3 | 98.9583% | 36.75 |
| 6 | 96.8750% | 37.80 |
| 12 | 70.4167% | 20.70 |
| 18 | 46.2500% | 0.00 |

The decline establishes a timing limitation within these instances even for the offline optimum. It does not establish online performance, real-network reliability, or superiority over published systems. Cost comparisons across rows have different achieved service levels and should not be interpreted as efficiency gains. Results and certificates are stored in `reference_results.json.gz`.

## Experimental data inspection

Six UE metric files from one ColO-RAN experimental run were retrieved from the source repository at commit `bd86629d07d5fbfb778ebe3afd9d0b05e5191c6b`. They contain 12,589 measurement rows in total. `radio_data_inspection.json` records individual source paths, original Git blob hashes, schemas, and descriptive summaries. The source is https://github.com/wineslab/colosseum-oran-coloran-dataset . Attribution and licensing remain with that repository.

The inspected data include channel quality, allocated PRBs, downlink buffers, throughput, and requested/granted PRBs. They do not contain individual packet ingress and end-to-end completion timestamps. Observed throughput cannot be equated with available service capacity when traffic demand is low. One experiment does not provide independent calibration and validation populations. No radio service envelope or deadline guarantee has been fitted or asserted from this inspection.

## Remaining scientific deliverables

Implement a causal controller whose reservations survive delayed execution, derive the guarantee under explicit service-envelope assumptions, establish its specific novelty, validate the service model on separate experiments, and perform fair external comparisons. The old manuscript remains a draft pending this work. The current reference and data inspection are reproducible foundations, not substitutes for these deliverables.

## Run

Requires NumPy and SciPy with `scipy.optimize.milp`.

```bash
python -m unittest discover -s redesign -p 'test_*.py' -v
python redesign/benchmark.py
```
