# Completed PRORL local experiment — 3 November 2026

The 89,400-step loop (86,400 training iterations plus 3,000 bootstrap steps) completed. The upstream previous-transition tracker records 89,399 transitions by design. Final evaluation completed on seeds 1000, 1100 and 1200, each for 168 steps. The validation-selected model was saved; the best validation iteration was 72, with utility 137.17999267578125 on validation seed 100. Training seed: 10. All 146 stored model-state tensors checked were finite.

## Matched synthetic comparison

These are upstream metric names and raw mean values over three evaluation seeds. They are not physical latency measurements. All environment fields except agent configuration and all emulator fields were checked equal. The original resource YAML was used to avoid recomputing allocations from an upstream-mutated configuration export.

| Policy | Utility reward | Remaining gap | Surplus | Cost | Hours satisfied | Resource utilization |
|---|---:|---:|---:|---:|---:|---:|
| prorl | 136.666672 | -93.333333 | 320.000000 | 18.666667 | 150.333333 | 0.904546 |
| random | -24.623335 | -1370.666667 | 261.000000 | 249.666667 | 0.000000 | 0.897806 |
| heuristic | 117.730003 | -248.666667 | 148.000000 | 231.000000 | 112.333333 | 0.951313 |
| greedy | 117.470001 | -248.333333 | 151.333333 | 233.000000 | 114.000000 | 0.950254 |

PRORL had higher utility and lower remaining-gap magnitude and cost in this run, but higher surplus and lower resource utilization than the heuristic and greedy policies. These tradeoffs must be reported together. No claim of uniform dominance is justified.

## Scope and next evidence

This is one trained seed on the upstream four-node synthetic constant-load scenario. PRORL is the published baseline, not a new thesis algorithm. The experiment does not establish a novel SDN-aware method, reproduce all paper settings, demonstrate real TIM workload performance, or provide multi-training-seed confidence intervals. Next work is an explicit paper-configuration audit, independent training seeds, held-out traffic scenarios and a specified SDN-aware extension with ablations. No manuscript submission was made.

## File integrity

```json
{
  "total_loop_steps": 89400,
  "recorded_previous_transitions": 89399,
  "evaluation_seeds": [
    1000,
    1100,
    1200
  ],
  "steps_per_evaluation_seed": 168,
  "finite_model_tensor_count": 146,
  "sha256": {
    "recovered_full.json": "7784faf699d74958cd07907c2364dd3d3cc03f3e7db620c77691cc5d0e939899",
    "recovered_full.pt": "a18c6bdbce234d4f8804da87b9d06eacf3f04b1a68bd7ef600b059bcb5fb8c01"
  }
}
```

The final archive includes the selected model, complete metrics, the last resumable checkpoint, source wrappers, original configuration files, compatibility patch, dependency versions, matched baseline outputs and SHA-256 manifest. The last checkpoint can precede the completed loop; use the final JSON/PT and completion audit as the completion evidence.

## Saved final artifacts

[PRORL_Completed_89400.zip](https://chatgpt.com/library?file_id=libfile_e01b5e33dd8081919cfeaded6e519ff7&account_id=personal)

Archive SHA-256: `3cd45ec542f9032c21c4c0d866dbf3e9bfd896a47a4bc05d3f44bce691fc8960`.
