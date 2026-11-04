"""Audit trusted local run artifacts and compare only matched evaluation metrics."""
import os
os.environ.update(ENV='test', FILTER_PATH='', DATA_BASE_DIR='data')
import sys, json, math, hashlib, copy
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'prorl_reproduction'
sys.path.insert(0, str(ROOT / 'baseline_prorl'))
import torch

def finite_json(x):
    if isinstance(x, dict):
        return all(finite_json(v) for v in x.values())
    if isinstance(x, list):
        return all(finite_json(v) for v in x)
    return not isinstance(x, float) or math.isfinite(x)

def tensors(x):
    if torch.is_tensor(x):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from tensors(v)
    elif isinstance(x, (tuple, list)):
        for v in x:
            yield from tensors(v)

def main():
    d = json.loads((P/'seed20_full.json').read_text())
    b = json.loads((P/'recovered_full.json').read_text())
    assert finite_json(d)
    c = d['config']
    assert c['random_seeds'] == dict(training=20, validation=[100], evaluation=[1000,1100,1200])
    assert c['run']['training_iterations'] == 86400
    assert c['environment']['agent']['double_dqn']['bootstrap_steps'] == 3000
    assert len(d['training/action_history/is_random']) == 89400
    assert d['training/total_steps'] == 89399
    matched = copy.deepcopy(c)
    matched['random_seeds']['training'] = 10
    assert matched == b['config']
    log = (P/'seed20_full.log').read_text()
    assert 'Evaluation completed: ' in log and '3/3' in log
    episodes = {}
    for seed in [1000,1100,1200]:
        prefix = f'evaluation-{seed}/'
        assert d[prefix+'episode/length'] == [168]
        assert len(d[prefix+'action_history/add']) == 168
        episodes[str(seed)] = dict(length=168, actions=168, utility=d[prefix+'reward/utility/total'])
    model = torch.load(P/'seed20_full.pt', map_location='cpu', weights_only=False)
    ts = list(tensors(model))
    assert ts and all(torch.isfinite(t).all().item() for t in ts)
    metrics = {k.removeprefix('evaluation/avg/'):dict(seed10=b[k][-1], seed20=v[-1], difference=v[-1]-b[k][-1]) for k,v in d.items() if k.startswith('evaluation/avg/') and '/times/' not in k}
    names = ['seed20_full.json','seed20_full.pt','seed20_full.checkpoint','seed20_full.log','train_seed20.py','checkpointing.py','supervise_seed20.py','environment.txt','compatibility.patch','verify_seed20_completion.py','recovered_full.json','recovered_full.pt']
    report = dict(seed=20, target_steps_including_bootstrap=89400, training_iterations=86400, bootstrap_steps=3000, observed_action_decisions=89400, tracker_previous_transition_count=89399, evaluation_completed=True, evaluation_episodes=episodes, all_result_numbers_finite=True, model_tensor_count=len(ts), all_model_tensors_finite=True, config_matches_seed10_except_training_seed=True, metrics=metrics, sha256={n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in names}, limitations=['Two training seeds only; three shared evaluation seeds.', 'Final weights selected using validation seed 100, not evaluation seeds.', 'Only the upstream constant-load scenario is covered; no general superiority or novelty established.', 'Tracker counts previous transitions; 89400 action decisions confirm the full configured loop.'])
    (P/'seed20_completion_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__ == '__main__':
    main()
