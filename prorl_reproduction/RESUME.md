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

## Episode-boundary recovery and local guard (2 November 2026)

The first full-run resume exposed a missing module-global TimeStep factory registry entry at the next episode reset. The short 160-step test had not crossed that boundary. `restore()` now registers the saved environment clock itself, without resetting its time. The recovered run passed episode boundaries and validation iteration 10 and wrote CHECKPOINT 12000. This is operational evidence, not a new full-run equivalence claim.

Source verification before recovery: upstream HEAD matched the pinned commit, the compatibility patch passed reverse-apply checking, both resume modules matched their published Git blob IDs before the clock fix, and all packages in environment.txt matched installed versions. Additional installed packages were cloudpickle 3.1.1 and dill 0.3.9.

A single locked local guard can monitor an existing flock-protected training process and resume if it exits:

```sh
baseline_prorl/.venv/bin/python prorl_reproduction/keep_training.py
```

The guard checks source/configuration hashes and installed package versions before each restart, never starts from scratch, prevents duplicate guards and training processes sharing these locks, and stops after three failed retries or if output files already exist. Output presence only hands control back to final validation; it is not a completion certificate. The guard depends on this host remaining alive; it cannot survive host termination.

A durable recovery snapshot at step 11000 is available as [PRORL_Recovery_11000.zip](https://chatgpt.com/library?file_id=libfile_917606a4906c8191a4b251a792f95fab&account_id=personal). It contains the trusted checkpoint, source wrappers, compatibility patch, dependency versions and SHA-256 manifest. It is an incomplete training snapshot, not final results.
