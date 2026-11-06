"""Matched new-seed evaluation of saved seed-30 checkpoint; no training."""
import copy
import hashlib
import json
import os
from pathlib import Path
import random
import sys
import re
from importlib.metadata import distributions

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'prorl_reproduction'
OUT = RUN / 'holdout_seed30'
SEEDS = list(range(2000, 2010))  # fixed before executing results


def main():
    OUT.mkdir(exist_ok=True)
    norm = lambda s: re.sub('[-_.]+', '-', s).lower()
    installed = {norm(d.metadata['Name']): d.version for d in distributions()}
    recorded = dict((norm(x.split('==')[0]), x.split('==')[1])
                    for x in (RUN/'environment.txt').read_text().splitlines() if '==' in x)
    assert all(installed.get(k) == v for k,v in recorded.items())
    (OUT/'runtime.json').write_text(json.dumps(dict(
        python=sys.version, recorded_packages_match=True,
        extra_packages={k:v for k,v in installed.items() if k not in recorded},
        note='Python 3.11.17 restored; package pins matched. Evaluation RNG reset to 10 to match seed-10 protocol.'),indent=2)+'\n')
    stats = json.loads((RUN/'seed30_full.json').read_text())
    audit = json.loads((RUN/'seed30_completion_verification.json').read_text())
    for name in ['seed30_full.json','seed30_full.pt']:
        expected = audit['sha256'][name]
        assert hashlib.sha256((RUN/name).read_bytes()).hexdigest() == expected
    assert not set(SEEDS) & set(stats['config']['random_seeds']['evaluation'])
    (OUT/'protocol.json').write_text(json.dumps(dict(
        evaluation_seeds=SEEDS, training_seed=30, new_training=False,
        source_model_sha256=audit['sha256']['seed30_full.pt'],
        scenarios='Same synthetic constant-load scenario; new random seeds only',
        agents=['prorl','greedy','heuristic']), indent=2)+'\n')
    sys.path.insert(0, str(ROOT/'baseline_prorl'))
    os.chdir(ROOT/'baseline_prorl')
    os.environ.update(ENV='test', FILTER_PATH='', DATA_BASE_DIR='data')
    import numpy as np
    import torch
    import yaml
    from prorl import SingleRunConfig
    from prorl.common.data_structure import RunMode
    from prorl.run.runner import TestRunner
    torch.set_num_threads(1)
    original = yaml.safe_load(Path('config/sensitivity_analysis/1-constant_load.yaml').read_text())['base_run_config']
    model = torch.load(RUN/'seed30_full.pt', map_location='cpu')
    outputs = {}
    for agent in ['prorl','greedy','heuristic']:
        raw = copy.deepcopy(stats['config'])
        raw['environment']['resources'] = copy.deepcopy(original['environment']['resources'])
        raw['environment']['agent']['type'] = agent
        raw['run']['run_mode'] = RunMode.Eval.value
        raw['random_seeds']['evaluation'] = SEEDS
        torch.manual_seed(10); random.seed(10); np.random.seed(10)
        config = SingleRunConfig(root_dir=str(ROOT/'baseline_prorl'), **raw)
        runner = TestRunner(run_code='holdout-seed30-'+agent, config=config)
        runner._init()
        if agent == 'prorl':
            runner.agent.load_agent_state(copy.deepcopy(model))
        runner.do_evaluations()
        result = runner.stats_tracker.disk_stats()
        assert result['config']['emulator'] == stats['config']['emulator']
        for key in stats['config']['environment']:
            if key != 'agent':
                assert result['config']['environment'][key] == stats['config']['environment'][key], key
        for seed in SEEDS:
            assert result[f'evaluation-{seed}/episode/length'] == [168]
            assert len(result[f'evaluation-{seed}/times/choose_action']) == 168
        outputs[agent] = result
        (OUT/(agent+'.json')).write_text(json.dumps(result, indent=2, default=lambda x: x.tolist() if hasattr(x,'tolist') else str(x)))
    metrics = ['reward/utility','reward/remaining_gap','reward/surplus','reward/cost','hour_satisfied','resource_utilization']
    summary = {a:{m:s['evaluation/avg/'+m][-1] for m in metrics} for a,s in outputs.items()}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print('HOLDOUT_COMPLETE', json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()

