# Frozen evaluation and publication decision

Read results_report/Simulation_Results_Report.pdf first. It contains the
independent results, plots and scientific-readiness audit. The underlying
frozen_results.json contains all 340 calibration and 320 held-out runs.

Reproduction:

```
python frozen_evaluation.py
python verify_frozen.py
python build_results_report.py
```

The frozen comparison selects among all 16 fixed additions using seeds
4000-4004 and evaluates on different seeds 5000-5019. Static selection requires
both calibration class means <=1%, choosing the least incremental cost. The
budget-matched comparator is selected using the calibration dynamic mean cost,
not by forcing identical realized held-out cost. Report both realized costs.

The earlier 80-81% claim only compared against permanent maximum expansion.
Compared with the independently selected adequate fixed expansion, the
held-out incremental-cost saving is 43.28% for transport stress, 42.62% for
compute stress and 38.82% for higher report delay/loss. These are abstract
incremental service-resource costs, not real money, energy or total network
cost. Classwise quality and exploratory paired intervals must accompany them.
No confirmatory superiority, equivalence or non-inferiority test is supplied.

Important distinction: these are final frozen outputs for this implemented
abstract model, not final publishable O-RAN results. The model still needs
calibrated radio/transport/compute service definitions and validation against
external evidence. Protocol implementation is not mandatory for every theory
paper, but its absence cannot be disguised as deployed O-RAN evidence.

All previous source and output files are retained. SHA256.json records current
file hashes (excluding itself). PNG chart exports accompany vector PDF plots.
