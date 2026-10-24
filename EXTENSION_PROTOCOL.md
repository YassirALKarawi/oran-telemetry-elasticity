# Locked extension protocol - 18 October 2026

This file is written before evaluating seeds 6000-6019 and 7000-7009.
It is a local design lock, not externally preregistered research.
The original calibration (4000-4004) and evaluation (5000-5019) remain unchanged.
The new seed ranges must never be used to tune a controller or select comparators.

## Primary replication and component isolation

Four existing settings, twenty seeds 6000-6019 and six variants give 480 runs.
Variants: full dynamic, round-robin telemetry, oldest-first telemetry, no backlog
prediction, no dispersion margin, and the previously selected fixed capacity.
All retain identical local scheduling, cost definition, action delay and report
budget. Fixed capacities are nominal (0,0), transport (2,0), compute (0,2), and
delayed/lost transport (2,0), inherited from calibration, never reselected.

## Exploratory activation-delay stress test

Transport stress, exactly ten seeds 7000-7009, report delay 3, loss
0.05, action delays 1, 5, 10, 25, 50, 100 slots. Full dynamic and fixed (2,0)
give 120 runs. Values span 20 ms to 2 s under the synthetic slot mapping.
The fixed capacity is preprovisioned but its share updates retain the same delay.
Delay zero is excluded because same-slot event ordering would need a new contract.

## Analysis before outcomes

Report every variant, both class miss rates, abstract incremental cost and all
six delay values. No best-seed or best-setting reporting. Seed is the independent
replication unit, packets within a seed are not assumed independent.
Use paired percentile bootstrap intervals with 10,000 resamples for differences
and savings versus fixed capacity. Mark intervals as exploratory, especially
near the zero-event boundary. Cost savings at zero fixed cost are undefined.

For full dynamic versus selected fixed in four settings and three metrics
(class 0, class 1, cost), report an exact paired sign test on nonzero differences
and Holm-adjust all 12 p-values as one family. This tests direction of paired
outcomes, not equality of means or noninferiority. No QoS equivalence claim.

If all 20 seed outcomes show no misses, report the exact one-sided 95% bound
1 - 0.05^(1/20) on the probability that a new seed-level run has any miss, under
i.i.d. seed-level sampling. Do not reinterpret it as a per-packet reliability bound.

## Verification versus validation

Independent simultaneous-step packet replay checks packet accounting, FIFO and
deadline boundaries against the production reverse-stage update. Independent
uncached finite-grid enumeration checks the cached optimizer. They do not
validate physical O-RAN behavior, radio propagation, CPU profiling or E2 messages.

## Decision gate

Negative ablation outcomes must constrain claims. No statistical result converts
the surrogate into a real deadline guarantee. The artifact is a computational
study and manuscript foundation, not three completed Q1 journal submissions.
