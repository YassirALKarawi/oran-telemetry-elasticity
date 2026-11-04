# Seed 20 recovery at step 62,000

The trainer and local supervisor were absent at inspection. The log ended at step 62,160; the locally generated checkpoint restored successfully with resume_index=62000, training seed 20, and target 89,400 steps including bootstrap. Final JSON and PT were absent. The cause of the interruption is not established.

Python 3.11.17 ran successfully, every pinned package matched environment.txt, and upstream commit 4c3c70c11e070e93c7077ce9f22f6ed9d9e178d2 and its diff hash matched holdout_seed10/verification.json. Training, checkpointing, environment, compatibility patch, and supervisor hashes also matched the previous audited files. See [audit](seed20_resume_62000_audit.json).

The existing bounded supervisor was started after the checks. Exactly one trainer was observed, with PID 18436 in the inspection namespace, and its log advanced to 62,328. The 160 logged steps after the checkpoint were recomputed. The supervisor cannot guarantee survival of host termination.

[Recovery archive, checkpoint, settings and SHA-256 manifest](https://chatgpt.com/library?file_id=libfile_f3fbea9754ac8191b0abcee71ac7de59&account_id=personal). Archive SHA-256: `912bf7a83981c48bdf909e63ed75047572146e397cf42f8082f2a5a200de8e00`.

Training and final evaluation are incomplete. No seed-20 result or superiority claim is made. Seed-10 artifacts are unchanged.
