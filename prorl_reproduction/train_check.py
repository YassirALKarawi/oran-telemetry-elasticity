"""Execute upstream PRORL's local evaluation path; not a paper reproduction."""
import os
import sys
import json
from pathlib import Path

upstream = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve()
agent_name = sys.argv[3] if len(sys.argv) > 3 else 'prorl'
sys.path.insert(0, str(upstream))
os.chdir(upstream)
os.environ['ENV'] = 'test'
os.environ['FILTER_PATH'] = ''
os.environ['DATA_BASE_DIR'] = 'data'
import yaml
from prorl import SingleRunConfig
from prorl.run.runner import TestRunner

raw = yaml.safe_load((upstream / 'config/sensitivity_analysis/1-constant_load.yaml').read_text())['base_run_config']
raw['environment']['agent']['type'] = agent_name
raw['random_seeds']['evaluation'] = [1000, 1100, 1200]
raw['redis']['enabled'] = False
raw['saver']['enabled'] = False
raw['emulator']['model']['tim_dataset_model_options'].pop('ran_configurations_path', None)
config = SingleRunConfig(root_dir=str(upstream), **raw)
runner = TestRunner(run_code='upstream-' + agent_name + '-smoke', config=config)
from prorl.common.data_structure import RunMode
config.run.run_mode = RunMode.Train
config.run.training_iterations = 512
config.run.validation_run.enabled = False
config.environment.agent.double_dqn.bootstrap_steps = 64
config.environment.agent.double_dqn.batch_size = 32
runner = TestRunner(run_code='prorl-training-check', config=config)
runner.run()
import torch
torch.save(runner.agent.get_agent_state(), output.with_suffix('.pt'))
output.write_text(json.dumps(runner.stats_tracker.disk_stats(), default=lambda x: x.tolist() if hasattr(x, 'tolist') else str(x), indent=2))
print('Evaluation completed:', output)
