# Verified training persistence

The checkpoint extension preserves the original off-policy loop ordering. It serializes the entire runner (including model, optimizer, replay buffers, environment, tracker and best validation model), loop variables, Python/NumPy/Torch CPU RNG states, and next step index. Writes use a temporary file, fsync and atomic replacement. The same pinned source and dependency environment are required. Load only trusted, locally created checkpoints: Python pickle is executable input.

Special reducers reconstruct upstream State arrays and metadata, namedtuple/dataclass records, and loggers. The loop is generated from the pinned upstream method with checked replacement markers. This is additional infrastructure, not an upstream feature or a new research algorithm.

Verification: a 160-step integration run, split at step 64 and restored in a new process, matched the uninterrupted run on all 220 non-timing recorded metrics. Training seeds were explicitly set to 10. Timing metrics and config were excluded from comparison. This test does not establish equivalence for every workload or future software version.

Full run (89,400 total steps including bootstrap) was restarted from scratch after the earlier process ended without a checkpoint. It retains validation and best-model selection. Every 1,000 steps a checkpoint is saved; this is not a completed experiment yet.

```sh
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 baseline_prorl/.venv/bin/python prorl_reproduction/train_resumable.py baseline_prorl prorl_reproduction/recovered_full.json prorl
# After a process interruption:
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 baseline_prorl/.venv/bin/python prorl_reproduction/train_resumable.py baseline_prorl prorl_reproduction/recovered_full.json prorl --resume
```

Never run both commands concurrently on the same checkpoint/output. The local CPU snapshot includes PyTorch optimizer/replay state rather than a weights-only warm restart. The final .pt stores the validation-selected model. JSON stores the effective configuration and original metrics. Full-budget completion, repeated independent training seeds, paper-level parameter matching, TIM data evaluation and a novel SDN-aware contribution remain unestablished. No submission-ready manuscript is claimed.
