# Deadline delivery on the emulated E2 transport fixture

The two policies replayed the same six frozen traces with the existing 16 Mbit/s shared budget. The decision rule, class weights, baseline, order and offered payload schedule were retained from the adaptive holdout. This is a fresh measurement on previously studied traffic. The endpoint counts unique packets received on time divided by all offered packets. Delay is application send to application receive on the same Linux monotonic clock. It excludes source waiting before send and control-plane time between windows. The receiver logs integer-ms upper-bound histograms. These give exact counts for each integer-ms cutoff. A missing packet is a deadline miss.

Primary thresholds project the synthetic model deadlines of 15 and 40 slots at 100 ms per slot (the transport report normalization interval). This is an experimental mapping, separate from the two-second traffic windows. Secondary 15/40 ms cutoffs probe sensitivity. Neither set represents a verified service requirement. Both profiles were frozen before this run.

Percentages below are the equally weighted means of six within-trace percentages. The combined column weights packets within each trace. Counts in the second table are pooled across traces.

| Profile | Group | Thesis on time (%) | Proportional on time (%) | Difference (pp) |
|---|---|---:|---:|---:|
| model_slot_projection | Class 1 | 77.101 | 65.860 | +11.241 |
| model_slot_projection | Class 2 | 50.637 | 64.310 | -13.673 |
| model_slot_projection | Both | 64.418 | 65.011 | -0.593 |
| tight_sensitivity | Class 1 | 53.472 | 42.129 | +11.343 |
| tight_sensitivity | Class 2 | 40.702 | 62.233 | -21.531 |
| tight_sensitivity | Both | 47.286 | 51.629 | -4.343 |

| Profile | Method | Class | Offered | On time | Late arrival | Missing |
|---|---|---:|---:|---:|---:|---:|
| model_slot_projection | thesis | 1 | 79750 | 61182 | 0 | 18568 |
| model_slot_projection | thesis | 2 | 72250 | 36171 | 0 | 36079 |
| model_slot_projection | proportional | 1 | 79750 | 52247 | 0 | 27503 |
| model_slot_projection | proportional | 2 | 72250 | 46054 | 0 | 26196 |
| tight_sensitivity | thesis | 1 | 79750 | 42110 | 19072 | 18568 |
| tight_sensitivity | thesis | 2 | 72250 | 28972 | 7199 | 36079 |
| tight_sensitivity | proportional | 1 | 79750 | 33248 | 18999 | 27503 |
| tight_sensitivity | proportional | 2 | 72250 | 44557 | 1497 | 26196 |

The test exercises two non-borrowing virtual links, local transport observations and an emulated radio endpoint. The six short traces describe the selected loads. No physical-radio or full network deadline was measured. The raw archive contains each window, the delay histograms, the per-trace scores, the packet capture and the 60 command acknowledgements. The audit was repeated on the downloaded artifact.

[Frozen code](https://github.com/YassirALKarawi/oran-telemetry-elasticity/tree/747e0da10188eceb74eea9296465786b1c2259b5/thesis_platform/deadlines) · [Run](https://github.com/YassirALKarawi/oran-telemetry-elasticity/actions/runs/42411161924) · [Evidence](./verified-42411161924.zip)

Archive SHA-256 `f5c712e6aba6a0f4ea22dbc7464d1d256205af391b84bee1947dfa3553bc3a13`.
