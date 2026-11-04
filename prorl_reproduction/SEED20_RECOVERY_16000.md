# Seed-20 recovery — 4 November 2026

The prior process was absent and the log ended at 16,632 steps. The locally generated checkpoint restored next_i=16,000, training seed 20 and total_steps=89,400. The original upstream revision and diff digest matched the recorded evaluation audit. Python 3.11.17 was restored; all recorded dependency versions matched. Training resumed with --resume under the per-output lock; a live Python process and advancing training log were observed. Work after the last checkpoint is recomputed.

Recovery archive: [PRORL_Seed20_Recovery_16000.zip](https://chatgpt.com/library?file_id=libfile_fdf82a5a454c819180b72d21f6fb79e6&account_id=personal).

The archive is an in-progress snapshot, not final results. seed20_resume_audit.json records the inspected checkpoint fingerprint and environment. An hourly conditional check was created to verify/resume training if accessible, save important checkpoints, validate completion and notify the user only for completion or meaningful changes/blockers. It must disable itself after completion notification. Scheduling does not guarantee access to the same workspace or continuous process survival. No completion or performance claim is made here.
