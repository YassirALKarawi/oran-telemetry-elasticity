# First common-environment check

This development run compares the thesis capacity/share optimizer from elastic.py with an immediate-service Greedy adapter in the synthetic radio–transport–compute tandem. Both use the existing work-conserving scheduler. The test isolates allocation by fixing telemetry requests to round robin for both controllers. The original adaptive report-selection mechanism is outside this test.

One 360-slot bursty-transport trace uses development seed 74103, identical arrivals and baseline capacities, one report request every five slots, three slots of telemetry delay, a shared 5% report-loss process and ten slots of command delay. The feasible actions have 0–3 extra units at each of transport and compute and a common two-class share on the 5% grid from 5% to 95%. The budget is a shared instantaneous ceiling. Realized expenditure can differ. Greedy maximizes immediate deadline-weighted service of reported backlog, with ties resolved by cheaper actions. PRORL's published Greedy comparator operates on a different action space.

At each decision both adapters receive the identical delayed reports, slot and previous target. Only the assigned policy controls its run. Closed-loop observations can consequently diverge between trajectories. The audit checks input immutability, action feasibility, application times, per-stage capacity and packet conservation. The packet ledger uses class, birth slot and within-slot sequence as its key. Empty delivery slots identify outstanding packets. There is unlimited buffering and no data-packet discard mechanism.

| Outcome | Thesis allocator | Greedy |
|---|---:|---:|
| Offered / delivered / outstanding | 1311 / 1304 / 7 | 1311 / 1304 / 7 |
| Deadline misses among 1204 packets whose deadline elapsed | 0 | 0 |
| Delivered-packet p99 delay in slots | 17 | 15 |
| Extra service unit-slots | 595 | 670 |
| Switched capacity units | 26 | 59 |

This trace exposes a cost–delay tradeoff. It supports integration testing. A comparative performance study needs prespecified independent scenarios, including tighter service regimes and a separate validation budget. Adapting PRORL to the common action space and verifying SDN/RIC actuation remain open.

Reproduce from the repository root with `python3 common_environment/pilot.py`. The runner writes the shared trace, results, two packet ledgers and two audits next to the script. Slot arrays encode time, cumulative offered, cumulative delivered, outstanding, available capacity by stage, and service by stage and class. Decision time in nanoseconds depends on the host. The remaining outputs are deterministic for the recorded implementation.
