# Common-environment acceptance gate

The current PRORL baseline transfers bandwidth resources between synthetic base stations. The thesis tandem-queue simulator selects telemetry reports and changes scheduling weights/elastic capacity; joint_allocation selects routes and processing destinations. These are different decision problems. Their rewards cannot be compared numerically, and neither action space can represent every action of the others.

Before an algorithm comparison, freeze one shared decision problem and implement an explicit adapter per policy. Every policy must receive the same observation fields and delays, feasible action set, resource budget, command execution delay, traffic traces and evaluation horizon. A policy requiring unavailable observations must be adapted and labelled accordingly. Published PRORL applied to a new action space must be labelled an adaptation, not an exact reproduction.

Required logged quantities: offered/admitted/delivered/lost/outstanding requests; end-to-end delay and deadline violations; transport and compute capacity use; resource-change cost; policy decision time; telemetry age and command application timestamps. Verify flow conservation and capacity constraints for every run. Preserve paired traces for all methods.

Model selection uses validation only. Keep the demand60/80/100 and seeds2000–2009 benchmark tests as disclosed diagnostics; since their results have already been examined, any method designed in response needs a fresh frozen test set. More training seeds improve replication but do not establish novelty.

Current status: interface requirements documented; no end-to-end policy adapter or matched thesis-versus-PRORL experiment completed. The existing Python simulators can support algorithm development; they do not demonstrate SDN/RIC deployment. Source references: thesis_platform/README.md, joint_allocation/README.md, ack_allocation/README.md and submission_work/oran_study/engine_v4.py.
