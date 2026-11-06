# Seed 40 completed training and matched frozen-model evaluation

Training: 89,400 decisions including bootstrap; seed 40; all 146 model tensors and all numeric results finite. Initial evaluation seeds 1000/1100/1200 each ran 168 steps; mean utility 137.04000854492188.

Extended evaluation: seeds 2000–2009, 168 steps each, at loads 60/80/100. The saved validation-selected model remained unchanged. No further training or evaluation-based selection. Evaluation seeds are episodes, not independent training runs.

| Demand | PRORL | Greedy | Heuristic |
|---|---:|---:|---:|
| 80 | 137.735992 | 116.669998 | 117.008995 |
| 60 | 104.847984 | 121.676010 | 121.677002 |
| 100 | 111.328003 | 110.843994 | 111.800003 |

All outcomes are retained, including losses against baselines. These results do not establish general superiority, novelty, thesis-method performance, SDN/RIC implementation, or paper readiness. The common-environment gate remains unresolved. Seed 50 is still required before the five-training-seed comparison.

[Complete model, results, configurations and checksums](https://chatgpt.com/library?file_id=libfile_9d6e9f6b8dac8191a096840f9f2d2be6&account_id=personal)
