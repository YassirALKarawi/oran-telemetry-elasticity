# Seed20 recovery at 41,000 — 4 November 2026

Inspection found no active trainer or supervisor. The log last recorded 41,832 steps and the checkpoint recorded 41,000. Final JSON/PT were absent. The local checkpoint restored seed 20, resume_index=41,000 and target=89,400. Source revision/diff and recorded package versions matched the reference audit; Python 3.11.17 executed.

The locked supervisor restarted training. A live trainer and advancing log to 41,328 were observed after resumption. Steps after the last saved checkpoint are recomputed; they do not constitute new progress beyond the pre-interruption maximum until that maximum is passed. The reason for the interruption is unconfirmed. This is not training completion.

[Persistent recovery archive](https://chatgpt.com/library?file_id=libfile_fb1a36555828819192e45a0d665027ab&account_id=personal). Archive includes checkpoint, source wrappers, dependency record, compatibility patch and SHA-256 manifest. See seed20_resume_41000_audit.json for validation details. No seed10 files were modified.
