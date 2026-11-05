"""Execute upstream PRORL's local evaluation path; not a paper reproduction."""
import os
import sys
import json
from pathlib import Path

SEED = 40
upstream = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve()
import fcntl
lock_handle = output.with_suffix('.lock').open('a')
fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
if '--resume' not in sys.argv and any(output.with_suffix(suffix).exists() for suffix in ('.json', '.pt', '.checkpoint')):
    raise RuntimeError('Existing run artifacts: inspect before starting or use --resume')
agent_name = sys.argv[3] if len(sys.argv) > 3 else 'prorl'
sys.path.insert(0, str(upstream))
os.chdir(upstream)
os.environ['ENV'] = 'test'
os.environ['FILTER_PATH'] = ''
os.environ['DATA_BASE_DIR'] = 'data'
import yaml
import torch
import random
import numpy as np
torch.manual_seed(SEED)
random.seed(SEED)
np.random.seed(SEED)
from prorl import SingleRunConfig
from prorl.run.runner import TestRunner

raw = yaml.safe_load((upstream / 'config/sensitivity_analysis/1-constant_load.yaml').read_text())['base_run_config']
raw['environment']['agent']['type'] = agent_name
raw['random_seeds']['training'] = SEED
raw['random_seeds']['evaluation'] = [1000, 1100, 1200]
raw['redis']['enabled'] = False
raw['saver']['enabled'] = False
raw['emulator']['model']['tim_dataset_model_options'].pop('ran_configurations_path', None)
config = SingleRunConfig(root_dir=str(upstream), **raw)
from prorl.common.data_structure import RunMode
config.run.run_mode = RunMode.Train
config.environment.episode.lives = 168
config.environment.agent.double_dqn.learning_rate = 0.005
config.environment.agent.double_dqn.batch_size = 256
runner = TestRunner(run_code='prorl-full-seed-40', config=config)
import torch
torch.set_num_threads(1)
from checkpointing import install, restore
install()
checkpoint = output.with_suffix('.checkpoint')
if '--resume' in sys.argv:
    runner = restore(checkpoint)
else:
    if '--test' in sys.argv:
        config.run.training_iterations = 128
        config.run.validation_run.enabled = False
        config.environment.agent.double_dqn.bootstrap_steps = 32
        config.environment.agent.double_dqn.batch_size = 16
        runner = TestRunner(run_code='resume-verification', config=config)
    runner.checkpoint_path = str(checkpoint)
    runner.checkpoint_every = 64 if '--test' in sys.argv else 1000
runner.stop_after_checkpoint = '--stop' in sys.argv
runner.run()
if runner.stop_after_checkpoint:
    sys.exit(0)
import torch
torch.save(runner.best_agent_model if runner.best_agent_model is not None else runner.agent.get_agent_state(), output.with_suffix('.pt'))
output.write_text(json.dumps(runner.stats_tracker.disk_stats(), default=lambda x: x.tolist() if hasattr(x, 'tolist') else str(x), indent=2))
print('Evaluation completed:', output)
