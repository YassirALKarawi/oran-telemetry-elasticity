# Scientific falsification audit, 2 November 2026

This audit precedes a research redesign. It does not change the frozen manuscript experiments and is not a new confirmation of the manuscript's contribution.

Question 1: can an optimistic scheduler overcome the offered traffic at the unactuated radio stage? Question 2: does a simple local earliest-deadline-first (EDF) scheduler change the ranking of the existing capacity controller?

Use seeds 24000--24019, the seven existing stress cases, and exactly six policies: risk/weighted, risk/EDF, static(2,0)/weighted, static(2,0)/EDF, maximum-capacity/weighted, maximum-capacity/EDF. For the compute case, rotate the static configuration as in the original protocol. The risk parameter remains 0.75. No parameter is selected from these audit results. Each policy receives identical arrivals, base capacities, report-loss flags, and activation delays. EDF is a local scheduling alternative with packet deadline access. The original scheduler already reads local queues and packet deadlines when lending residual capacity. EDF does not receive future arrivals or extra capacity.

The maximum-capacity policy uses the original engine's always_on configuration, with capacity (0,3,3) active from time zero. It is a deliberately expensive capability benchmark, not a cost-matched competitor. Its share decisions use the same fixed-capacity solver as the original engine. Static policies use the original static configuration and share solver.

Primary descriptive outputs: mean class-specific deadline misses, abstract capacity cost, paired cost differences, and all per-seed outcomes. No p-value-based claim of novelty or superiority will be made from this exploratory audit. All results, including unfavorable ones, are retained.

An independent optimistic relaxation discards all non-cohort traffic and all downstream capacity constraints. A packet born at b with end-to-end deadline D must receive radio service no later than b+D-3 because the original three-stage engine requires two subsequent service slots. Match unit packets to available radio service units between b and b+D-3. Greedy EDF with expired-job deletion maximizes the number matched in this single-stage interval matching problem. Its unmatched packet count is a lower bound on total end-to-end misses of every controller with the same radio capacity, even with perfect information, instantaneous actuation elsewhere, and unlimited downstream resources. This is a trace-specific aggregate bound, not a classwise guarantee or a claim of a novel scheduling theorem. Verify the implementation against independent maximum bipartite matching on small random cases before running the audit.

Retain SHA-256 digests of this protocol and the audit code in the result artifact. Do not overwrite existing reliability_results.json or use audit data for a later confirmatory evaluation.
