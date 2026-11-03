# Demand-shift evaluation and independent training status

4 November 2026. Saved training-seed-10 model evaluated without retraining at synthetic demand_absolute_value=60 and 100, versus the training configuration's 80. Ten evaluation seeds (2000–2009) and 168 steps per episode were used for each of PRORL, Greedy and Heuristic: 60 episodes / 10,080 new evaluation steps.

The amplitudes were fixed before these runs. These same evaluation seeds were already used in the preceding same-load diagnostic, so this is paired exploratory stress testing, not a fresh untouched confirmatory test set. No tuning was performed from these results.

| Demand parameter | Policy | Utility | Surplus | Utilization |
|---|---|---:|---:|---:|
| 60 | PRORL | 106.000000 | 925.5 | 0.723433 |
| 60 | Greedy | 121.676010 | 160.7 | 0.932882 |
| 60 | Heuristic | 121.677002 | 162.3 | 0.932330 |
| 100 | PRORL | 108.964005 | 8.6 | 0.997428 |
| 100 | Greedy | 110.843994 | 2.7 | 0.999161 |
| 100 | Heuristic | 111.800003 | 0.5 | 0.999851 |

These are upstream synthetic reward/resource metrics. The saved model's higher utility at the original amplitude did not persist at either changed amplitude. In particular the low-demand case exposes a large surplus. This is a generalization limitation, not proof of the cause, not a new algorithm and not real network evidence. Do not omit the unfavorable cases.

The evaluator explicitly loads the saved model, restores original resource YAML and checks identical non-agent environment fields. The emulator comparison permits only the declared demand amplitude change. Observation/action interface loading succeeded and each episode length and action count was checked. No reward was redesigned or model retrained. Complete outputs, runtime details, protocols and hashes are in demand_shift_60/ and demand_shift_100/. Runtime restoration has the same disclosed limitations as holdout_seed10/README.md.

## Independent training replication

A separate seed-20 training run was launched on the original demand=80 configuration using train_seed20.py. The total target remains 89,400 steps including 3,000 bootstrap steps. Its output stem is seed20_full; the seed-10 artifacts are untouched. A per-output advisory lock rejects a concurrent duplicate. Starting without --resume rejects existing JSON/PT/checkpoint files.

At this status check the process and advancing log were observed, the 3,000-step checkpoint existed, and an early recovery snapshot was saved:
https://chatgpt.com/library?file_id=libfile_16661dcf90e481919738292a1bc45d92&account_id=personal

This run is IN PROGRESS, not completed or evaluated. Process survival across workspace maintenance is not guaranteed. The snapshot is a recovery artifact, not a final model or result. Preserve the original upstream checkout, compatible environment and patch when restoring. Do not load untrusted pickle checkpoints.

From repository root, after verifying no existing process owns this run:

    OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 baseline_prorl/.venv/bin/python -u prorl_reproduction/train_seed20.py baseline_prorl prorl_reproduction/seed20_full.json prorl --resume

The seed-20 source changes all initial RNG seeds and random_seeds.training to 20. Validation/evaluation seeds and the optimization budget stay matched. A second training seed is an initial replication, not a statistically adequate campaign by itself. Do not evaluate learning quality from bootstrap rewards.

Current source and runtime checks from the preceding evaluation remain available in holdout_seed10/verification.json and runtime.json. Future completion requires final JSON/PT, completed evaluation, finite tensors and artifact hashes before any completion claim.
