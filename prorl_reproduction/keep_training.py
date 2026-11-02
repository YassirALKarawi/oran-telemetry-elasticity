"""Guard one trusted local run. This guard cannot outlive a terminated host.

Run from the project root using the already verified Python environment.
Checks local source/configuration and installed distribution versions before
each retry. Does not start from scratch or change the training budget.
"""
import fcntl
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'prorl_reproduction'
os.chdir(ROOT)


def fingerprint():
    paths = [RUN / 'train_resumable.py', RUN / 'checkpointing.py']
    paths += sorted((ROOT / 'baseline_prorl/prorl').rglob('*.py'))
    paths += sorted((ROOT / 'baseline_prorl/config').rglob('*.yaml'))
    return {
        'files': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in paths},
        'python': sys.version,
        'packages': sorted((d.metadata['Name'], d.version)
                           for d in importlib.metadata.distributions()),
    }


def has_outputs():
    return any((RUN / ('recovered_full' + ext)).exists() for ext in ('.json', '.pt'))


def main():
    # A distinct lock prevents two guards; the training lock is shared with
    # direct flock-protected launches and is inherited by every child.
    with (RUN / 'recovered_full.guard.lock').open('a') as guard:
        try:
            fcntl.flock(guard, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        expected = fingerprint()
        failures = 0
        with (RUN / 'recovered_full.lock').open('a') as lock:
            while failures < 3:
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    time.sleep(30)
                    continue
                try:
                    if has_outputs():
                        print('Outputs present: leave final validation to monitoring task.', flush=True)
                        return
                    if fingerprint() != expected:
                        raise RuntimeError('Source or environment changed; refusing automatic resume')
                    if not (RUN / 'recovered_full.checkpoint').is_file():
                        raise RuntimeError('Trusted checkpoint missing; refusing fresh training')
                    print('Resuming trusted checkpoint', flush=True)
                    env = dict(os.environ, OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
                    with (RUN / 'recovered_full.log').open('ab', buffering=0) as log:
                        result = subprocess.run(
                            [str(ROOT / 'baseline_prorl/.venv/bin/python'),
                             'prorl_reproduction/train_resumable.py', 'baseline_prorl',
                             'prorl_reproduction/recovered_full.json', 'prorl', '--resume'],
                            env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                            pass_fds=(lock.fileno(),), check=False)
                    if result.returncode == 0:
                        if not has_outputs():
                            raise RuntimeError('Runner exited without output files')
                        return
                    failures += 1
                    print(f'Runner exit {result.returncode}; retry {failures}/3', flush=True)
                finally:
                    fcntl.flock(lock, fcntl.LOCK_UN)
                time.sleep(30 * failures)
        raise RuntimeError('Three failed resumes; inspect log before retrying')


if __name__ == '__main__':
    main()
