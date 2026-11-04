# Seed 20 recovery at step 79,000

Neither trainer nor supervisor was running at inspection. Last logged iteration: 79,128. The local checkpoint restored with resume_index=79000, seed 20 and target 89,400 including bootstrap. Final JSON and PT were absent. Interruption cause remains unknown.

Python 3.11.17 executed successfully; every pinned package matched environment.txt. Upstream commit 4c3c70c11e070e93c7077ce9f22f6ed9d9e178d2 and the diff hash matched holdout_seed10/verification.json. Training, supervisor, checkpointing, environment and compatibility-patch hashes matched the previous audit. See [audit](seed20_resume_79000_audit.json).

A detached supervisor launch did not remain alive after its command returned; the training lock was free and the log unchanged. The existing bounded supervisor was then started in a retained execution session. Exactly one trainer (PID 28434 in the inspection namespace), its supervisor and a held training lock were observed. The log advanced to 79,464, beyond the previous 79,128. The 128 steps after the checkpoint were recomputed. Host termination cannot be prevented by the local supervisor.

[Recovery checkpoint, settings and SHA-256 manifest](https://chatgpt.com/library?file_id=libfile_1655a997395c819185ba46a65bdef3fe&account_id=personal). Archive SHA-256: `99decdec32f8be4cdc8cb9e43ba8effff9eb530d46fbed4281d813ed1c0a63ad`.

Training and final evaluation remain incomplete. No final seed-20 result or general superiority claim is made. Seed-10 outputs are unchanged.
