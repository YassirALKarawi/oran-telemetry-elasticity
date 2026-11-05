# Matched PRORL evaluation across training seeds and demand shifts

Two frozen models trained independently with seeds 10 and 20; no new training or model selection. Evaluation seeds 2000–2009, 168 steps per episode. Evaluation initialization RNG resets remain 10 for every agent, matching the original seed-10 evaluation protocol. The three scenarios were fixed in advance: constant demand amplitudes 80, 60 and 100. Baseline summary values match exactly across the two evaluations. Seed20 adds 90 episodes and 15,120 evaluation actions; only 30 episodes and 5,040 actions use the learned PRORL model. These are not additional training seeds.

| Demand | PRORL seed10 | PRORL seed20 | Greedy | Heuristic |
|---|---:|---:|---:|---:|
| 80 | 137.120 | 137.768 | 116.670 | 117.009 |
| 60 | 106.000 | 105.402 | 121.676 | 121.677 |
| 100 | 108.964 | 111.512 | 110.844 | 111.800 |

Both learned models exceed the reference utilities at demand 80, but both fall below them at demand 60. At demand 100 seed20 exceeds Greedy slightly and remains below Heuristic, while seed10 falls below both. This supports scenario-dependent behavior, not broad superiority. Surplus at demand60 is 925.5 (seed10), 927.0 (seed20), versus 160.7 for Greedy; the observed surplus is a plausible contributor to the lower composite utility, not a causal ablation result.

Two training seeds are insufficient for reliable between-training-run uncertainty. More independent training runs remain necessary. The thesis method still requires a shared environment, reward, observation/action budget and validation-only model selection before comparison against PRORL. The original thesis simulator rewards cannot be numerically compared to these utilities. This report is a benchmark result, not a claim of methodological novelty or a submission-ready manuscript.

[Full evaluation package](https://chatgpt.com/library?file_id=libfile_88880cf779a481918b1630692a4a297f&account_id=personal).
