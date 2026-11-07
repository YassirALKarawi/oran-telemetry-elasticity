"""Match the saved seed-50 model to the validation-selected state in the last trusted checkpoint."""
from hashlib import sha256
import json
import os
from pathlib import Path
import pickle
import sys

root = Path(__file__).resolve().parents[1]
run = root/'prorl_reproduction'
sys.path[:0] = [str(root/'baseline_prorl'), str(run)]
os.chdir(root/'baseline_prorl')
os.environ.update(ENV='test', FILTER_PATH='', DATA_BASE_DIR='data')
import torch
import checkpointing

def tensor_map(item, path=()):
    if torch.is_tensor(item):
        yield path, item
    elif isinstance(item, dict):
        for k,v in item.items():
            yield from tensor_map(v,path+(k,))
    elif isinstance(item, (list,tuple)):
        for i,v in enumerate(item):
            yield from tensor_map(v,path+(i,))

p=run/'seed50_full.checkpoint'
audit_file=run/'seed50_completion_verification.json'
audit=json.loads(audit_file.read_text())
log=(run/'seed50_full.log').read_text()
assert 'CHECKPOINT 89000' in log and 'Evaluation completed:' in log
with p.open('rb') as f:
    payload=pickle.load(f)
runner=payload['runner']
assert runner.config.random_seeds.training == 50 and payload['next_i']==89000
assert runner.best_validation_performance_iteration == audit['best_validation_iteration']
assert runner.best_validation_performance == audit['best_validation_utility']
selected=dict(tensor_map(runner.best_agent_model))
saved=dict(tensor_map(torch.load(run/'seed50_full.pt',map_location='cpu',weights_only=False)))
assert len(saved)==audit['counts']['tensors'] and selected.keys()==saved.keys()
assert all(torch.equal(v,selected[k]) for k,v in saved.items())
audit.update(validation_model_tensor_match=True,final_checkpoint_step=89000,
             final_checkpoint_sha256=sha256(p.read_bytes()).hexdigest())
audit_file.write_text(json.dumps(audit,indent=2)+'\n')
print('Verified selected tensors',len(saved), 'validation iteration', audit['best_validation_iteration'])
