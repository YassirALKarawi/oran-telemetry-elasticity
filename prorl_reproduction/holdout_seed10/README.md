# Saved PRORL: new-seed evaluation

4 November 2026. Completed evaluation only: 30 episodes, 168 steps each (5,040 evaluation steps), zero new training steps.

The saved seed-10 model was explicitly loaded into the evaluation agent. Evaluation seeds 2000–2009 were fixed in the script and protocol before results were obtained. These differ from the previous evaluation seeds 1000,1100,1200 and validation seed 100. They are additional randomness within the same four-node synthetic constant-load scenario, not held-out traffic families or real-network validation.

| Mean metric | PRORL | Greedy | Heuristic |
|---|---:|---:|---:|
| Utility | 137.120010 | 116.669998 | 117.008995 |
| Signed remaining gap | -98.4 | -251.7 | -247.6 |
| Surplus | 301.7 | 155.6 | 157.9 |
| Cost | 19.4 | 235.8 | 236.1 |
| Hours satisfied | 149.4 | 115.2 | 116.4 |
| Utilization | 0.910005 | 0.949219 | 0.948591 |

All are upstream synthetic metric definitions, not physical latency, energy or provisioning measurements. Mean paired utility differences were +20.450007 against Greedy and +20.111005 against Heuristic, positive on all ten evaluation seeds. Surplus remains higher and utilization lower, so no uniform dominance is claimed. The checkpoint comes from one training seed; these episodes do not estimate training variability, establish novelty, or validate SDN integration.

## Runtime recovery and matching

The existing virtual environment initially referenced a missing Python interpreter. A normal uv Python installation restored Python 3.11.17. All package versions listed in environment.txt matched installed versions. Additional packages cloudpickle 3.1.1 and dill 0.3.9 were present. The original interpreter patch version was not established, so this is not a claim of an identical complete runtime. runtime.json records the actual interpreter.

The saved model and training-results hashes matched completion_audit.json. The original resource YAML was used as in compare_completed.py to avoid reusing the upstream-mutated derived allocation export. The script asserts equality of emulator configuration and all non-agent environment fields with the completed run. It records source revision and diff digest in verification.json. Episodes and action counts were checked. No training loop was called.

## Files and execution

Run from repository root:

    OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 baseline_prorl/.venv/bin/python prorl_reproduction/evaluate_saved_holdout.py

prorl.json, greedy.json and heuristic.json retain the complete upstream evaluation outputs, including configuration and histories. protocol.json records seeds and scope; summary.json contains mean metrics; verification.json contains paired utilities, counts and SHA-256 hashes. The source model remains in the completed-run archive linked by ../COMPLETED_RUN.md. Rerunning requires that model, original source/configuration and compatible dependencies.

The next evidence gap is independent training seeds and held-out traffic scenarios, followed by a specified new algorithm with matched comparisons. This evaluation reuses the completed baseline and supplies no new thesis contribution on its own.
