# PRORL reproduction checkpoint

Status: dependency installation succeeded; initialization failed. No paper result has been reproduced.

Reference: PRORL: Proactive Resource Orchestrator for Open RANs Using Deep Reinforcement Learning, IEEE TNSM 21(4), 3933–3944, 2024. DOI: https://doi.org/10.1109/TNSM.2024.3373606

Upstream: https://github.com/AlessandroStaffolani/prorl-orchestrator
Pinned commit: `4c3c70c11e070e93c7077ce9f22f6ed9d9e178d2`.

Python 3.11.17 and the upstream pinned requirements were installed, using torch 2.1.0+cpu. The full resolved environment is recorded in environment.txt.

The proposed smoke test uses the upstream constant-load configuration, random agent, evaluation seed 1000, and local TestRunner with saving and Redis disabled. It is a software test, not PRORL training or reproduction of a published improvement.

Observed initialization issues:
1. FILTER_PATH and DATA_BASE_DIR must be set before importing prorl.
2. Default initialization looks for `data/models/tim_dataset/sub_area-top_12_nodes.json`; the shipped file is at `data/models/sub_area-top_12_nodes.json`. A local symlink was added.
3. SingleRunConfig references missing ModelConfig fields `nodes_demand_model_options` and `auto_configurable_model_options`. A diagnostic patch removes the stale assignment loop. This is not validated as a faithful reproduction patch.
4. After that patch, initialization fails on missing `AgentType.is_mc_method`. The latest traceback is in smoke.log. That method is also referenced by rollouts.py, so replacing it with an arbitrary constant could change evaluation behavior and has not been done.

Run after resolving and validating upstream compatibility:

```sh
baseline_prorl/.venv/bin/python prorl_reproduction/smoke.py baseline_prorl prorl_reproduction/smoke_results.json
```

Next gate: reconcile the missing APIs against the paper and repository history; establish a valid upstream run before introducing research changes. The paper remains a candidate baseline. A code initialization failure does not invalidate the published paper.
