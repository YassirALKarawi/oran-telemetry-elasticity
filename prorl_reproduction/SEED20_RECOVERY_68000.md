# Seed 20 recovery at step 68,000

At inspection no trainer or supervisor process was present. Last logged iteration: 68,208; checkpoint resume_index: 68,000; training seed: 20; target: 89,400 including bootstrap. Final JSON and PT were absent. The interruption cause is unknown.

Checkpoint restoration succeeded under executable Python 3.11.17. Every pinned environment package matched; upstream commit 4c3c70c11e070e93c7077ce9f22f6ed9d9e178d2 and the diff hash matched holdout_seed10/verification.json. Training, supervisor, checkpointing, environment and compatibility-patch hashes matched the previous audited source. See [audit](seed20_resume_68000_audit.json).

Started the existing bounded supervisor after verification. One trainer (PID 20203 in the inspection namespace) and its supervisor were observed; the training lock was held. The 208 logged steps after the checkpoint require recomputation. Host termination cannot be prevented by the local supervisor.

[Recovery checkpoint, settings and SHA-256 manifest](https://chatgpt.com/library?file_id=libfile_0c2e0429e0ac819199bdf0a2589d5ee7&account_id=personal). Archive SHA-256: `0ba4851db6973ec9dfed4a17a8131c8c57f6d15c7f0572fc1cfdac46c35ea137`.

Training and final evaluation remain incomplete. No final seed-20 performance or general superiority claim is made. Seed-10 outputs were not changed.
