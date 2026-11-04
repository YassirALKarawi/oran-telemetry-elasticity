# PRORL seed 20: completed training and matched evaluation

Verified on 4 November 2026. Training seed 20 completed 89,400 action decisions: 86,400 configured training iterations plus 3,000 bootstrap steps. The tracker reports 89,399 previous transitions by implementation design. Evaluation completed on seeds 1000, 1100 and 1200, each with one 168-step episode (504 evaluation actions). These are evaluation seeds, not additional independent training runs.

All 146 tensors in the final model and all numeric JSON results are finite. The final model was selected using validation seed 100; the log records its best validation performance at validation iteration 69. The retained restart checkpoint is at 89,000 and is not the final selected model; use seed20_full.pt for the verified evaluation artifact.

## Matched comparison against training seed 10

The complete configurations match except for the training seed. Both use the same validation seed and evaluation seeds, budgets and upstream constant-load scenario. The table compares evaluation averages only.

| Evaluation metric | Seed 10 | Seed 20 | Seed 20 minus seed 10 |
| --- | ---: | ---: | ---: |
| reward/utility | 136.666672 | 136.573318 | -0.093353 |
| reward/remaining_gap | -93.333333 | -93.333333 | +0.000000 |
| reward/surplus | 320.000000 | 322.666667 | +2.666667 |
| reward/cost | 18.666667 | 17.333333 | -1.333333 |
| problem_solved/count | 150.333333 | 151.333333 | +1.000000 |
| hour_satisfied | 150.333333 | 151.666667 | +1.333333 |
| resource_utilization | 0.904546 | 0.903720 | -0.000826 |
| episode/length | 168.000000 | 168.000000 | +0.000000 |

Utility is approximately 0.0683% lower for seed 20. The remaining-gap total is equal; surplus is slightly higher, while reallocation cost is slightly lower. This mixed result does not establish that one seed is better overall. Two independent training seeds and three shared evaluation episodes are insufficient to establish broad superiority or robustness. No significance claim is made. The published PRORL baseline does not establish thesis novelty.

The seed-10 additional holdout evaluation and load-shift tests remain separate: seed 20 has not yet received those additional tests. Do not pool seed-10-only extra tests with this matched comparison. The pre-existing thesis simulator uses different mechanics/rewards, so these utilities must not be numerically compared with its rewards. Next steps are matched seed-20 holdout/load-shift evaluation, more independent training seeds, and a common environment for any new thesis method and baselines.

## Provenance and recovery

Upstream commit: 4c3c70c11e070e93c7077ce9f22f6ed9d9e178d2. Diff SHA-256: 6b4c93254a7a01236a1c8a2ed0adf0ad518ee3d1de8d9c98afda985dde2f5fcb. Python 3.11.17 and all pinned environment packages matched before the final resume. The final resume used the locally generated checkpoint at 88,000; repeated host/session interruptions occurred, and unsaved steps were recomputed. This was not an uninterrupted run.

The archive contains final JSON and PT, log, last recovery checkpoint, configuration, environment pins, training/checkpoint/supervisor/audit scripts, compatibility patch, provenance checks, and seed-10 JSON/PT for the matched comparison. SHA-256 values are in seed20_completion_verification.json and manifest.json. Neither a journal submission nor a novelty claim is implied.

[Download the verified final archive](https://chatgpt.com/library?file_id=libfile_8ebb0c11d9888191a163da5974b5c9a8&account_id=personal).

Archive SHA-256: `8be4facd622b00d2df06fea2737ccef581a8593c6a72958a595f4e22ababd6cb`.
