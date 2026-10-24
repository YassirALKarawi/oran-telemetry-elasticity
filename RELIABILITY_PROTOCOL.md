# Reliability-screened extension, frozen 22 October 2026

No new calibration or evaluation result has been inspected when this protocol is
written. No parameter may be retuned on evaluation results. This is a locally
frozen design, not external preregistration.

Primary target: each class's mean seed-level deadline miss fraction <=0.001
(0.1%). Calibration selection uses a one-sided 95% percentile bootstrap upper
bound, separately in two report-delay/loss strata. A zero bootstrap bound from
zero observed misses is not a distribution-free guarantee of zero risk.
Paired reliability margin is 0.001 (0.1 percentage points), prespecified.
The term reliability-screened does not mean exact equality of true reliability.

Calibration: seeds 12000-12005, periodic transport, L=10. Two strata are (R=3,
p=.05) and (R=9,p=.15). Sixteen fixed expansions and four settings for each of
three adaptive families yield 336 executions. Fixed profiles include all
(x2,x3) in {0,1,2,3}^2. Risk headroom eta={.25,.5,.75,1}, HPA-inspired target
utilization={.55,.7,.85,.95}, DPP-adapted cost weight={.1,.3,1,3}.
Select the lowest mean-cost eligible configuration separately for each family.
If none qualifies, retain the declared conservative fallback only as diagnostic
and label the family calibration-ineligible. Adaptive candidates have four
tuning choices each. Fixed uses the full sixteen-profile feasible grid.

Held-out evaluation: seeds 13000-13019, seven settings, six methods, 840 runs.
Settings: periodic transport R3/p.05/L10, Markov-modulated transport R3/p.05/L10,
compound-Poisson Markov transport R3/p.05/L10, periodic compute R3/p.05/L10,
periodic transport R9/p.15/L10, periodic transport R3/p.05/L50, and jittered
actuation with delays independently sampled from {1,5,10,25,50} and R3/p.05.
Markov low-to-high probability .005 and high-to-low .02 per slot. High arrivals
(1.8,3.8), low (.9,2.1). Compound arrivals batch size3, arrival-event intensity
divided by3 to preserve conditional means. Transport base capacity3 in high
state, else5+choice(-1,0,0,1). No workload is an operator trace.

Methods: calibrated action-ledger risk proxy, calibrated fixed, HPA-inspired
adaptation, drift-plus-penalty-inspired adaptation, uncalibrated ledger eta1,
and no-ledger ablation with the calibrated eta. All use identical traces,
request budgets, report loss flags, action options and local scheduler. The
fixed profile's transport/compute components are exchanged for compute stress.
No tuning on distribution-shift settings. Jitter delay is announced upon command
submission, commands are not cancelled, and an older command can activate after
a newer one. All methods receive the same activation schedule.

Report every family, failure and class. Bootstrap resampling uses independent
seeds, 10000 draws, two-sided95% mean intervals and one-sided95% paired upper
bounds. Paired noninferiority screening is descriptive and unadjusted across
settings. Do not assert familywise noninferiority. A cost advantage is qualified
only if the risk-policy absolute reliability screen and paired reliability screen
both pass in the setting. Ordinary performance plots include all methods.
No physical O-RAN, energy, monetary, stability or probability guarantee is claimed.
