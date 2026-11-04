# Seed20 recovery at 36,000 — 4 November 2026

No trainer/supervisor process was found at inspection. The last logged checkpoint was 36,000; final JSON/PT were absent. The locally generated checkpoint loaded successfully with resume_index=36,000, seed=20 and target=89,400. Source revision and diff digest matched holdout_seed10/verification.json; Python 3.11.17 executed and every recorded package version matched environment.txt.

Training resumed through the locked bounded supervisor without a duplicate. This is an in-progress recovery, not completion. The restart cause was not established; a local supervisor cannot survive loss of its execution environment.

[Recovery archive](https://chatgpt.com/library?file_id=libfile_11a3f72765948191b57e82349856601e&account_id=personal). Fingerprints and restored state metadata are in seed20_resume_36000_audit.json. The seed10 model and results were not changed.
