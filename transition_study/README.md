# Transition-aware placement: initial exact mechanism test

This is an exploratory three-service, two-destination model, not a completed paper or realistic O-RAN benchmark. The hypothesis is that selecting a final resource allocation jointly with its transition schedule can recover feasibility lost by optimizing steady-state placement first.

The comparator is deliberately strong: it selects minimum steady-state cost and then solves the transition exactly for all tied placements. The joint method solves both decisions by exhaustive enumeration. State-copy bandwidth competes with live traffic, source resources persist until completion, and destination resources are allocated from copy start. A fixed minimum transfer duration is calculated from identical state volume and destination-specific reserved transfer rate. Slot rounding may reserve unused final-slot bandwidth.

## Executed outcome

All 40 seeds 51000--51039 are retained. Joint planning found feasible schedules in 40 cases. The sequential comparator found feasible schedules in 38. The joint method therefore recovered two otherwise infeasible transitions. Among the 38 paired feasible instances, cost saving was zero. This is not evidence of a general cost advantage or publication-level novelty. By construction the joint feasible set contains the sequential method's feasible set, so weak dominance alone is not a research contribution.

Verification independently checked 255 returned candidate schedules for state transfer volume, CPU occupancy, shared migration bandwidth, temporary compute, mixed live/copy destination traffic, and lifetime resource cost. Two destinations have deliberately different prices and transfer rates. Setup, acknowledgment and cutover times are zero, source network resources are assumed sufficient, and service continuity is an assumption under the capacity model. No packet-level latency, radio behavior, measured downtime or SDN interface has been evaluated.

An implementation correction before the reported result made transfer duration consistent with the same state volume at both destinations. Only the corrected model is represented by results.json. The protocol and experiment remain exploratory. Future confirmation must use new instances after the design is fixed.

## Run

```bash
python transition_study/experiment.py
```

The next scientific question is whether transition feasibility gains survive realistic setup/cutover timing, uncertainty, and comparisons against existing transition-aware methods. No new submission-ready manuscript is claimed.
