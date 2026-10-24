# Paper protocol locked before seeds 9000-9019

18 October 2026. Earlier development seeds 8000-8004 showed that action-ledger
projection and a bounded dispersion horizon alone do not resolve long command
delays. Those 40 development runs remain visible and are not test evidence.

The proposed deployment policy is a delay-gated controller. If the configured
actuation delay is at least the shorter class deadline (15 slots), use the
previously calibrated fixed capacity from the start of the run. Otherwise use
action-ledger projection and a five-slot dispersion margin. This is a deployment
gate for a fixed delay configuration, not an online detector of varying latency.
The gate does not guarantee deadlines or improve the calibrated fixed policy.

Fixed profiles, selected on seeds 4000-4004 before all present outcomes, are
nominal (0,0), transport (2,0), compute (0,2), and delayed/lost transport (2,0).
No fixed profile, threshold, margin or objective coefficient may be retuned on
the new evaluation seeds. Any future redesign needs a new protocol and seed set.

Eight settings: the four original settings at activation delay 10, plus ordinary
transport stress at activation delays 1,25,50,100. Five methods: legacy elasticity,
ungated pipeline elasticity, gated pipeline elasticity, bounded-margin-only
ablation and the calibrated fixed reference. Twenty seeds 9000-9019 yield 800
executed policy runs. Every setting uses identical exogenous traces and report
losses across methods. Identical gated/fixed outcomes in long-delay settings
are expected by construction and must not be presented as independent discovery.

Primary metrics: classwise measured-arrival-cohort miss rate and full-run
incremental resource/switching cost. No energy, financial or URLLC claims.
Use 10,000 paired seed-bootstrap resamples for differences, exact sign tests
with ties excluded, and Holm correction over all 48 comparisons (8 settings,
2 comparators,3 endpoints). Statistical tests assess paired direction, not
noninferiority or mean equivalence. Retain both classes and every negative case.

Formal statements are conditional correctness or fallback-equivalence statements.
No uncalibrated dispersion surrogate is presented as a probabilistic guarantee.
The paper is a simulation study under explicit abstractions, not field validation.
