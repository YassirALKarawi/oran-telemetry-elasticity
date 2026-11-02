# Nonzero phase timing and stronger comparison

Sixty exploratory instances were executed on seeds 52000--52019. Setup, acknowledgment and cutover durations were each 0, 1 or 2 synthetic slots. These durations are not measurements or a reconstruction of MOVE-CU. The accepted-manuscript link on the publisher site returned only a waiting page, so no physical timing calibration was asserted.

| Phase durations | Joint feasible | Transition-screened feasible | Steady-first feasible | Strict cost wins over screened | Mean paired saving |
|---|---:|---:|---:|---:|---:|
| 0,0,0 | 20/20 | 20/20 | 20/20 | 0 | 0% |
| 1,1,1 | 13/20 | 13/20 | 12/20 | 1 | 0.05784% |
| 2,2,2 | 1/20 | 1/20 | 1/20 | 0 | 0% |

The stronger comparator examines transition feasibility for every final placement, selects minimum steady-state cost among feasible placements, and then optimizes its transition exactly. It is an explicit comparison design, not a reproduction of a published system. Joint and screened methods have identical feasibility by construction. The single cost improvement does not demonstrate a strong general advantage. High phase delays make most cases infeasible under the common 12-slot transition deadline, and those outcomes are retained.

Independent verification reconstructed resource occupancy and full lifetime cost for all 234 returned feasible candidate schedules. It checked consistent transfer volume, phase timing, CPU, shared copy bandwidth, destination live/copy bandwidth, and temporary duplication. The result is a falsification/sensitivity experiment, not publication-ready validation. This candidate should not be promoted as a strong novel resource-allocation contribution on current evidence.

Reproduce with `python transition_study/phased.py` and `python transition_study/verify_phased.py`. Full records are in `phased_results.json.gz`.
