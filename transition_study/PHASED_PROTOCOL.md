# Timing sensitivity protocol

Use all seeds 52000--52019, a 12-slot transition horizon, and a 20-slot resource lifetime. Setup, readiness acknowledgment and cutover each take either zero, one or two slots. These are illustrative stress parameters, not measured milliseconds or seconds. Hold all other generation rules fixed. Evaluate 60 instances without tuning or discarding outcomes.

The final allocation is checked for steady-state feasibility. Each schedule then reserves destination CPU from setup start, copying bandwidth only during state transfer, destination live bandwidth from copying completion, and source CPU through acknowledgment and cutover completion. Temporary duplicate CPU spans setup through cutover. Source transport capacity is assumed sufficient. Dirty-state synchronization, packet-level loss, control-message failures and radio channels remain unmodeled.

Compare exact joint optimization with (a) minimum steady-state placement followed by exact scheduling and (b) transition-aware feasibility screening of every placement, choosing lowest steady-state cost among feasible placements, then minimum transition cost among ties. Comparator (b) has the same feasible placement set as joint optimization, so its feasibility necessarily matches. Its difference is objective ordering, not information or algorithmic weakness. It is an explicitly defined baseline, not a claimed reproduction of a published system.

Report all feasibility counts and paired costs against (b). A negative result means this small model does not support the proposed cost advantage. The zero-phase stratum isolates the effect of timing assumptions.
