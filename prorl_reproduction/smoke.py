"""Execute upstream PRORL's local evaluation path; not a paper reproduction."""
import os
import sys
import json
from pathlib import Path

upstream = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(upstream))
os.chdir(upstream)
os.environ['ENV'] = 'test'
os.environ['FILTER_PATH'] = ''
os.environ['DATA_BASE_DIR'] = 'data'
import yaml
from prorl import SingleRunConfig
from prorl.run.runner import TestRunner

raw = yaml.safe_load((upstream / 'config/sensitivity_analysis/0-constant_load-baselines.yaml').read_text())['base_run_config']
raw['environment']['agent']['type'] = 'random'
raw['random_seeds']['evaluation'] = [1000]
raw['redis']['enabled'] = False
raw['saver']['enabled'] = False
config = SingleRunConfig(root_dir=str(upstream), **raw)
runner = TestRunner(run_code='upstream-random-smoke', config=config)
runner._init()
runner.do_evaluations()
output.write_text(json.dumps(runner.stats_tracker.disk_stats(), default=lambda x: x.tolist() if hasattr(x, 'tolist') else str(x), indent=2))
print('Evaluation completed:', output)
