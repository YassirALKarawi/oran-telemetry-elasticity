# Seed20 recovery at 47,000 — 4 November 2026

No trainer/supervisor process was found at inspection. Last logged iteration was 47,376, and the last complete checkpoint was 47,000. Final JSON/PT were absent. The local checkpoint restored resume_index=47,000, training seed=20 and target=89,400. Python 3.11.17, recorded package versions, upstream revision and source-diff digest were checked against prior records and matched.

The locked bounded supervisor restarted training. Work after the saved checkpoint is recomputed. Restart cause remains unconfirmed; repeated process loss shows that the local supervisor alone does not guarantee continuous execution in this environment. No completion or evaluation result is claimed.

[Persistent checkpoint archive](https://chatgpt.com/library?file_id=libfile_0447f4644d2c819188109a3a8871ef64&account_id=personal). It includes source wrappers, dependency record, compatibility patch and SHA-256 manifest. Details are in seed20_resume_47000_audit.json. The completed seed10 artifacts remain unchanged.
