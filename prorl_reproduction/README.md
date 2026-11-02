# PRORL local reproduction checkpoint

Reference: PRORL: Proactive Resource Orchestrator for Open RANs Using Deep Reinforcement Learning, IEEE TNSM 21(4), 3933–3944, 2024. https://doi.org/10.1109/TNSM.2024.3373606

Upstream: https://github.com/AlessandroStaffolani/prorl-orchestrator
Pinned commit: `4c3c70c11e070e93c7077ce9f22f6ed9d9e178d2`.

## Executed

Local upstream TestRunner evaluations completed for random, heuristic and greedy policies, each with seeds 1000, 1100 and 1200: nine episodes of 168 steps on four nodes (1512 total steps). Inputs start from the upstream constant-load sensitivity configuration. Full effective configuration and metrics are included in each results JSON. This is an integration smoke test, not reproduction of the paper's trained PRORL results, not a new method and not a publication claim.

Python 3.11.17, torch 2.1.0+cpu, and the original pinned dependencies were installed. environment.txt records resolved dependencies.

## Compatibility changes

The repository history was fetched (six commits). Current source contains stale references to removed components. compatibility.patch is a local repair, not an author-approved patch:
- Remove assignments to two nonexistent model-configuration fields and branches for absent TestModel.
- Remove imports/mappings for absent models; retain synthetic and TIM model implementations.
- Supply explicit classification of the six registered agents as non-Monte-Carlo and non-policy-gradient. Unknown names raise rather than silently default. This routes these agents to the existing step-based evaluator.
- Replace the removed SamplingOptimal enum in the greedy superclass initializer with the registered Greedy identifier. The subclass already sets its name to Greedy.

No reward, environment-transition, synthetic-demand or DQN learning formula was modified. Evaluation routing is a compatibility assumption still requiring paper-level validation. The wrapper removes a null, unused TIM path from the synthetic configuration and sets the documented environment variables. A symlink resolves the packaged metadata location.

## Re-run

Clone upstream, checkout the pinned commit, create a Python 3.11 environment and install requirements (CPU PyTorch is sufficient). Then, from the project root:

```sh
git -C baseline_prorl apply ../prorl_reproduction/compatibility.patch
mkdir -p baseline_prorl/data/models/tim_dataset
ln -s ../sub_area-top_12_nodes.json baseline_prorl/data/models/tim_dataset/sub_area-top_12_nodes.json
baseline_prorl/.venv/bin/python prorl_reproduction/smoke.py baseline_prorl prorl_reproduction/random_results.json random
baseline_prorl/.venv/bin/python prorl_reproduction/smoke.py baseline_prorl prorl_reproduction/heuristic_results.json heuristic
baseline_prorl/.venv/bin/python prorl_reproduction/smoke.py baseline_prorl prorl_reproduction/greedy_results.json greedy
```

The earlier attempted_compatibility.patch records the first failed attempt and is superseded by compatibility.patch. Do not apply both. summary.json contains unaltered upstream metric names; they are not percentages of improvement or physical latency measurements. Timings are host-dependent.

Next gate: validate configuration and metric definitions against the paper, run the original PRORL training/validation procedure and recover comparable published results before designing the thesis extension. Real TIM workloads and SDN orchestration integration have not been evaluated here.
