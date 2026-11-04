# Seed 20 recovery at step 73,000

At inspection neither trainer nor supervisor was running. The log ended at 73,920; the checkpoint restored with resume_index=73000, training seed 20 and target 89,400 including bootstrap. Final JSON and PT were absent. The interruption cause remains unknown.

Python 3.11.17 executed successfully; every package pinned in environment.txt matched. Upstream commit 4c3c70c11e070e93c7077ce9f22f6ed9d9e178d2 and its diff hash matched holdout_seed10/verification.json. Training, supervisor, checkpointing, environment and compatibility-patch hashes matched the prior audited files. See [audit](seed20_resume_73000_audit.json).

The existing bounded supervisor was started after verification. Exactly one trainer (PID 22393 in the inspection namespace) and its supervisor were observed, with the training lock held. The restarted log advanced from 73,080 to 73,248. It must recompute 920 previously logged steps after the checkpoint. The local supervisor cannot prevent host termination.

[Recovery checkpoint, settings and SHA-256 manifest](https://chatgpt.com/library?file_id=libfile_6adc70dfca648191ad846557bb21beac&account_id=personal). Archive SHA-256: `a70fabf55ac6c2c983ad9169524462bdb2f18f3aef87aa82b3f24e14a692181d`.

Training and final evaluation remain incomplete. No seed-20 final performance or general superiority claim is made. Seed-10 outputs are unchanged.
