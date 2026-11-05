"""Sequential, resumable local replication; does not survive host termination."""
import os, sys, json, time, fcntl, hashlib, subprocess, re, math
from pathlib import Path
from importlib.metadata import distributions
ROOT = Path(__file__).resolve().parents[1]
P = ROOT/'prorl_reproduction'

def complete(seed):
    result = P/f'seed{seed}_full.json'
    model = result.with_suffix('.pt')
    if not result.exists() or not model.exists():
        return False
    d = json.loads(result.read_text())
    assert d['config']['random_seeds']['training'] == seed
    assert len(d['training/action_history/is_random']) == 89400
    for s in [1000,1100,1200]:
        assert d[f'evaluation-{s}/episode/length'] == [168]
    assert math.isfinite(d['evaluation/avg/reward/utility'][-1])
    # Final weights require a separate tensor/provenance audit before publishing.
    return True

def main():
    guard=(P/'remaining_seeds.lock').open('a')
    fcntl.flock(guard,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert sys.version_info[:3] == (3,11,17)
    norm=lambda x:re.sub('[-_.]+','-',x).lower()
    installed={norm(d.metadata['Name']):d.version for d in distributions()}
    for line in (P/'environment.txt').read_text().splitlines():
        if '==' in line:
            n,v=line.split('==');assert installed.get(norm(n))==v,n
    expected=json.loads((P/'FIVE_SEED_PROTOCOL.json').read_text())
    assert subprocess.check_output(['git','-C',str(ROOT/'baseline_prorl'),'rev-parse','HEAD'],text=True).strip()==expected['source']
    assert hashlib.sha256(subprocess.check_output(['git','-C',str(ROOT/'baseline_prorl'),'diff','HEAD'])).hexdigest()==expected['diff_sha256']
    for seed in [30,40,50]:
        attempts=0
        while not complete(seed):
            lock=(P/f'seed{seed}_full.lock').open('a')
            try:
                fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:
                lock.close();time.sleep(20);continue
            lock.close()
            result=P/f'seed{seed}_full.json'
            if result.exists() or result.with_suffix('.pt').exists():
                raise RuntimeError(f'Partial final artifacts for seed {seed}; inspect before retry')
            attempts+=1
            assert attempts<=3, f'Seed {seed}: three attempts exhausted'
            cmd=[sys.executable,'-u',str(P/f'train_seed{seed}.py'),str(ROOT/'baseline_prorl'),str(result),'prorl']
            if result.with_suffix('.checkpoint').exists():cmd+=['--resume']
            env=os.environ.copy();env.update(OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
            print('START',seed,'attempt',attempts,'resume','--resume' in cmd,flush=True)
            with (P/f'seed{seed}_full.log').open('a') as log:
                status=subprocess.call(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
            print('EXIT',seed,status,flush=True)
            if status!=0:time.sleep(20)
        print('TRAINING_AND_EVALUATION_ARTIFACTS_PRESENT',seed,flush=True)
    print('QUEUE_FINISHED_REQUIRES_FINAL_AUDIT',flush=True)

if __name__=='__main__':main()
