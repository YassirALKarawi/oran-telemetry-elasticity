"""Persist the complete runner and loop state, including replay buffers and RNGs.

Only load checkpoints created locally by this experiment.
"""
import inspect
import os
import random
import textwrap
from pathlib import Path
import pickle as dill
import copyreg
import numpy as np
import torch
import prorl.run.runner as upstream
from prorl.common.logger import BaseLogger, get_logger
from prorl.core.state import StateFeature, State
from prorl.core.step import Step
from prorl.environment.action_space import Action
from prorl.environment.agent.experience_replay.replay_buffer import ExperienceEntry
import dataclasses

copyreg.pickle(BaseLogger, lambda value: (get_logger, (value.logger_config,)))
copyreg.pickle(StateFeature, lambda value: (StateFeature, tuple(value)))
copyreg.pickle(Step, lambda value: (Step, tuple(value)))
def reduce_dataclass(value):
    return type(value), tuple(getattr(value, f.name) for f in dataclasses.fields(value))
copyreg.pickle(Action, reduce_dataclass)
copyreg.pickle(ExperienceEntry, reduce_dataclass)
def restore_state(array, attrs):
    value = array.view(State)
    value.__dict__.update(attrs)
    return value
copyreg.pickle(State, lambda value: (restore_state, (np.asarray(value), vars(value))))

FIELDS = ('previous_state', 'previous_action', 'step_info', 'reward',
          'episode_stats', 'n_episodes', 'done', 'state')

def save_checkpoint(runner, local):
    path = Path(runner.checkpoint_path)
    payload = dict(runner=runner, loop={k: local[k] for k in FIELDS},
                   next_i=local['current_i'] + 1, python_rng=random.getstate(),
                   numpy_rng=np.random.get_state(), torch_rng=torch.get_rng_state())
    tmp = path.with_suffix('.tmp')
    with tmp.open('wb') as stream:
        dill.dump(payload, stream)
        stream.flush()
        os.fsync(stream.fileno())
    tmp.replace(path)
    print('CHECKPOINT', payload['next_i'], flush=True)

def restore(path):
    with open(path, 'rb') as stream:
        payload = dill.load(stream)
    random.setstate(payload['python_rng'])
    np.random.set_state(payload['numpy_rng'])
    torch.set_rng_state(payload['torch_rng'])
    runner = payload['runner']
    # The upstream factory registry is module-global and is not pickled with
    # the runner. Reattach the restored clock before the next episode reset.
    # Keep the saved clock object and its position; do not create a new clock.
    from prorl.core.timestep import time_step_instances
    time_step_instances[runner.env.run_code] = runner.env.time_step
    runner.resume_loop = payload['loop']
    runner.resume_index = payload['next_i']
    return runner

def install():
    source = textwrap.dedent(inspect.getsource(upstream.BaseRunner.train_off_policy))
    marker = '    for current_i in range(self.total_steps):'
    assert source.count(marker) == 1
    start = source.index('    self._pre_run_start(')
    end = source.index(marker)
    original_init = source[start:end]
    restore_code = "    if hasattr(self, 'resume_loop'):\n"
    for key in FIELDS:
        restore_code += f"        {key} = self.resume_loop[{key!r}]\n"
    restore_code += '        start_i = self.resume_index\n    else:\n'
    restore_code += textwrap.indent(original_init, '    ')
    restore_code += '        start_i = 0\n'
    source = source[:start] + restore_code + source[end:]
    source = source.replace(marker, '    for current_i in range(start_i, self.total_steps):')
    point = '        state = next_state\n'
    assert source.count(point) == 1
    source = source.replace(point, point + '''        if (current_i + 1) % self.checkpoint_every == 0:
            save_checkpoint(self, locals())
            if getattr(self, 'stop_after_checkpoint', False):
                return
''')
    scope = dict(vars(upstream), save_checkpoint=save_checkpoint)
    exec(compile(source, '<checkpointed-upstream-loop>', 'exec'), scope)
    upstream.BaseRunner.train_off_policy = scope['train_off_policy']
