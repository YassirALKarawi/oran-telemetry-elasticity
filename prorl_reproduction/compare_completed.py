"""Audit a completed local PRORL run and evaluate matched baseline settings.

This is a single-training-seed synthetic integration comparison, not a claim
of paper reproduction, novelty, or statistically established superiority.
Run only after recovered_full.json and recovered_full.pt are complete.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'prorl_reproduction'
sys.path.insert(0, str(ROOT / 'baseline_prorl'))
os.chdir(ROOT / 'baseline_prorl')
os.environ.update(ENV='test', FILTER_PATH='', DATA_BASE_DIR='data')
import numpy as np
import torch
import yaml
from prorl import SingleRunConfig
from prorl.common.data_structure import RunMode
from prorl.run.runner import TestRunner


def audit(stats):
    assert 'Evaluation completed: ' in (RUN / 'recovered_full.log').read_text()
    assert stats['training/total_steps'] == 89399  # upstream records previous transition
    c = stats['config']
    assert c['run']['training_iterations'] + c['environment']['agent']['double_dqn']['bootstrap_steps'] == 89400
    assert c['random_seeds']['evaluation'] == [1000, 1100, 1200]
    for seed in c['random_seeds']['evaluation']:
        assert len(stats[f'evaluation-{seed}/times/choose_action']) == 168
        assert stats[f'evaluation-{seed}/episode/length'] == [168]
    for key, values in stats.items():
        if key.startswith('evaluation') and isinstance(values, list) and values:
            assert np.isfinite(np.asarray(values, dtype=float)).all(), key
    state = torch.load(RUN / 'recovered_full.pt', map_location='cpu')
    count = 0
    def visit(x):
        nonlocal count
        if isinstance(x, torch.Tensor):
            assert torch.isfinite(x).all(), 'Nonfinite model tensor'
            count += 1
        elif isinstance(x, dict):
            for v in x.values(): visit(v)
        elif isinstance(x, (list, tuple)):
            for v in x: visit(v)
    visit(state)
    assert count > 0
    return {'total_loop_steps': 89400, 'recorded_previous_transitions': 89399,
            'evaluation_seeds': [1000, 1100, 1200], 'steps_per_evaluation_seed': 168,
            'finite_model_tensor_count': count,
            'sha256': {n: hashlib.sha256((RUN/n).read_bytes()).hexdigest()
                       for n in ['recovered_full.json', 'recovered_full.pt']}}


def main():
    torch.set_num_threads(1)
    stats = json.loads((RUN / 'recovered_full.json').read_text())
    evidence = audit(stats)
    results = {'prorl': stats}
    for agent in ['random', 'heuristic', 'greedy']:
        raw = copy.deepcopy(stats['config'])
        # Upstream mutates the shared resource-class allocation dictionary
        # during setup. Reconstruct resource inputs from the original YAML,
        # rather than feeding the mutated export through ResourceConfig's
        # derived-allocation calculation a second time.
        original = yaml.safe_load((ROOT / 'baseline_prorl/config/sensitivity_analysis/1-constant_load.yaml').read_text())['base_run_config']
        raw['environment']['resources'] = copy.deepcopy(original['environment']['resources'])
        raw['environment']['agent']['type'] = agent
        # Preserve the complete environmental, reward, demand and evaluation
        # configuration. Only policy selection and execution mode differ.
        raw['run']['run_mode'] = RunMode.Eval.value
        torch.manual_seed(10); random.seed(10); np.random.seed(10)
        config = SingleRunConfig(root_dir=str(ROOT / 'baseline_prorl'), **raw)
        runner = TestRunner(run_code='matched-' + agent, config=config)
        runner._init()
        runner.do_evaluations()
        result = runner.stats_tracker.disk_stats()
        assert result['config']['emulator'] == stats['config']['emulator']
        for key in [k for k in stats['config']['environment'] if k != 'agent']:
            assert result['config']['environment'][key] == stats['config']['environment'][key], (key, result['config']['environment'][key], stats['config']['environment'][key])
        (RUN / ('matched_' + agent + '.json')).write_text(json.dumps(result, indent=2, default=lambda x: x.tolist() if hasattr(x, 'tolist') else str(x)))
        results[agent] = result
    metrics = ['reward/utility', 'reward/remaining_gap', 'reward/surplus',
               'reward/cost', 'problem_solved/count', 'hour_satisfied',
               'resource_utilization', 'episode/length']
    summary = {a: {k: s['evaluation/avg/' + k][-1] for k in metrics}
               for a, s in results.items()}
    (RUN / 'completion_audit.json').write_text(json.dumps(evidence, indent=2))
    (RUN / 'matched_comparison.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps({'audit': evidence, 'comparison': summary}, indent=2))


if __name__ == '__main__':
    main()
