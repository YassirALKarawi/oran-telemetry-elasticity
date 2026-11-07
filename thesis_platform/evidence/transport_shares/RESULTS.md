# Closed-loop transport share development trial

[Verified run 42409105984](https://github.com/YassirALKarawi/oran-telemetry-elasticity/actions/runs/42409105984) used workflow revision c71a23e7fe2ff73b50afe4a32ffdd893b6e12c96 and the pinned FlexRIC revision in the [evidence archive](./verified-42409105984.zip). SHA-256 of the archive is d99d715b68ca52d44f4de9ccfb63833a3bbaffa12cd46392b1f5444c10ad1e0f.

The project allocator in elastic.py selected transport shares on its original 5% grid, using measured prior-window sender and receiver counts and four Linux queue backlog samples per class. Local host observations fed the controller directly. The resource envelope was fixed at 16 Mbit/s. Capacity expansion was disabled. Radio and compute reports were idle placeholders with capacity 100. Each window's quantities were normalized to 0.1-second service units, with a one-slot forecast horizon and zero variance input. The experiment tests the share decision in isolation.

The xApp encoded each decision in a lab extension of the FlexRIC MAC example. After receipt and acknowledgement on E2, the experiment adapter applied the share decoded by the node to two non-borrowing Linux token buckets. Both policies used that path. Every applied class rate was checked against the kernel. The capture contains 20 requests and 20 acknowledgements across both policies. The allocator read transport counters out of band. The test used emulated radio endpoints and no external SDN controller.

Two paired replays used the same offered payload schedule in reverse policy order. Each arm started at 50/50. Three two-second windows offered 12/3 Mbit/s across the two classes, followed by three at 3/12. Measurement and control took place between windows. Each receiver counted unique 1,000-byte UDP payloads. The reference kept both classes at 8 Mbit/s. Aggregate configured capacity was identical each window.

| Delivery metric | Thesis | Equal split |
|---|---:|---:|
| Class 1, delivered/offered | 20,374/22,500 (90.55%) | 16,122/22,500 (71.65%) |
| Class 2, delivered/offered | 13,196/22,500 (58.65%) | 16,122/22,500 (71.65%) |
| Both classes | 33,570/45,000 (74.60%) | 32,244/45,000 (71.65%) |

The class-1 share sequence was 50%, 90%, 90%, 90%, 40%, 40% in each thesis replay. The first window after the load reversal inherited the previous 90% share. Only 402 of 3,000 class-2 packets arrived in that window, compared with 1,937 under equal splitting. Aggregate delivery improved by 2.95 percentage points while class-2 delivery fell by 13.00 points. The two replays repeat one development trace and give no independent scenario-level precision estimate. A matched adaptive baseline and independent traces are needed for algorithm ranking. This run establishes closed-loop actuation on the software transport fixture. It does not test full cross-domain allocation, physical radio performance, or deadline compliance.

The original [incomplete attempt](https://github.com/YassirALKarawi/oran-telemetry-elasticity/actions/runs/42408766844) stopped on the upstream MAC example's action-42 restriction. The final experiment patch records the changes to both service-model endpoints and the emulator.
