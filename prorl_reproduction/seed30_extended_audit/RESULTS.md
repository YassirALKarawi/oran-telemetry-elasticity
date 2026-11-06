# Seed 30: completed training and matched extended evaluation

Training: 89,400 decisions including bootstrap; 146 finite model tensors; initial evaluation seeds 1000/1100/1200, each 168 steps.

Extended evaluation: frozen validation-selected model; seeds 2000–2009, 168 steps each; evaluation RNG reset to 10, same protocol as seeds 10 and 20. No additional training. All numeric results are finite; model SHA-256 unchanged.

| Demand | PRORL seed 30 | Greedy | Heuristic |
|---|---:|---:|---:|
| 80 | 135.896011 | 116.669998 | 117.008995 |
| 60 | 104.503990 | 121.676010 | 121.677002 |
| 100 | 109.305992 | 110.843994 | 111.800003 |

These are results within the PRORL simulator, not evidence of thesis-method superiority or novelty. Retain unfavorable demand-shift outcomes. The ten evaluation seeds are not ten independent training runs. Seeds 40 and 50 remain pending; five-training-seed aggregation is premature. Common thesis/baseline environment and SDN/RIC integration remain incomplete.

Final model, results, settings and checksums: https://chatgpt.com/library?file_id=libfile_5fe3f587cfbc81918d95a01d089c7280&account_id=personal

Seed 40 checkpoint at 7000 and seed 30 initial artifacts: https://chatgpt.com/library?file_id=libfile_b7d780821bf08191aefebdacaf613b39&account_id=personal
