"""Bounded local restart supervisor. Does not survive loss of its host."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from importlib.metadata import distributions

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'prorl_reproduction'


def main():
    guard = (RUN/'seed20_supervisor.lock').open('a')
    fcntl.flock(guard, fcntl.LOCK_EX | fcntl.LOCK_NB)
    norm = lambda s: re.sub('[-_.]+', '-', s).lower()
    installed = {norm(d.metadata['Name']): d.version for d in distributions()}
    recorded = dict((norm(x.split('==')[0]),x.split('==')[1])
                    for x in (RUN/'environment.txt').read_text().splitlines() if '==' in x)
    assert all(installed.get(k) == v for k,v in recorded.items())
    reference = json.loads((RUN/'holdout_seed10/verification.json').read_text())
    revision = subprocess.check_output(['git','-C',str(ROOT/'baseline_prorl'),'rev-parse','HEAD'],text=True).strip()
    diff = subprocess.check_output(['git','-C',str(ROOT/'baseline_prorl'),'diff','HEAD'])
    assert revision == reference['upstream_commit']
    assert hashlib.sha256(diff).hexdigest() == reference['upstream_diff_sha256']
    tracked = ['train_seed20.py','checkpointing.py','environment.txt']
    hashes = {n:hashlib.sha256((RUN/n).read_bytes()).hexdigest() for n in tracked}
    for attempt in range(1,4):
        for n,h in hashes.items():
            assert hashlib.sha256((RUN/n).read_bytes()).hexdigest() == h
        probe = (RUN/'seed20_full.lock').open('a')
        try:
            fcntl.flock(probe,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            print('Existing trainer owns lock; supervisor exits without duplicate.',flush=True)
            return
        finally:
            probe.close()
        if (RUN/'seed20_full.json').exists() or (RUN/'seed20_full.pt').exists():
            print('Final artifact present: manual completion audit required; no restart.',flush=True)
            return
        assert (RUN/'seed20_full.checkpoint').is_file()
        env=os.environ.copy();env.update(OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
        command=[sys.executable,'-u',str(RUN/'train_seed20.py'),str(ROOT/'baseline_prorl'),str(RUN/'seed20_full.json'),'prorl','--resume']
        print('Resume attempt',attempt,flush=True)
        with (RUN/'seed20_full.log').open('a') as log:
            process=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
            print('Child PID',process.pid,flush=True)
            status=process.wait()
        print('Trainer exit',status,flush=True)
        if status == 0:
            return
        if attempt < 3:
            time.sleep(30)
    raise RuntimeError('Three exits; stop restart loop and inspect logs')


if __name__ == '__main__':
    main()
