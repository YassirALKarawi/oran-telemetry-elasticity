# Adaptive transport-share comparison

Six new traffic traces and the primary endpoint were committed before execution. Each of the three load families has two seeded rate sequences and opposite policy order. Each trace has six two-second windows. Both arms start at 50/50, may choose the same 19 discrete shares, and use two non-borrowing Linux token buckets with a combined 16 Mbit/s rate. Decisions use completed-window observations and take effect the next window. Both arms pass through the same emulated E2 control path. Linux counters and queue samples supply the observations directly.

The existing thesis share solver runs with fixed capacity, idle radio/compute reports, a one-slot prediction horizon and zero variance input. Its original class deadline weights are retained. The baseline rounds the prior window's measured fraction of offered packets to the nearest allowed share. The source supplies the same packet size, count, and nominal send times for the two arms of each pair. Runtime pacing is subject to host scheduling. The artifact records actual window times.

Percentages are calculated within each trace first and averaged across six paired traces with equal weight. A transition window is the first window with a different dominant class from its predecessor. The first window of a trace is excluded from that secondary endpoint.

| Metric, % | Thesis | Proportional | Paired difference, pp |
|---|---:|---:|---:|
| Overall delivery (primary) | 64.41 | 65.01 | -0.60 |
| Class 1 delivery | 77.08 | 65.86 | +11.22 |
| Class 2 delivery | 50.64 | 64.31 | -13.67 |
| Delivery in first windows following a change in dominant class | 52.78 | 47.94 | +4.84 |

| Trace | Family | Thesis delivered/offered | Proportional delivered/offered | Difference, pp |
|---:|---|---:|---:|---:|
| 871201 | persistent | 17708/25000 | 19889/25000 | -8.72 |
| 871202 | persistent | 18200/23500 | 18145/23500 | +0.23 |
| 871203 | alternating | 12883/27000 | 12498/27000 | +1.43 |
| 871204 | alternating | 14994/24500 | 13460/24500 | +6.26 |
| 871205 | mixed | 16355/26750 | 17141/26750 | -2.94 |
| 871206 | mixed | 17198/25250 | 17165/25250 | +0.13 |

Independent archive checks matched all 72 ledger rows to the frozen input schedule, all 60 decisions to the node's decoded events, and all 60 requests and acknowledgements to the capture. The rates applied to both classes were also checked against Linux by the trial. The six selected short traces on one Linux runner provide descriptive transport-share results. They do not estimate general radio performance, end-to-end deadline compliance, or performance against PRORL. No training or post-result parameter selection was used.

[Protocol and implementation](https://github.com/YassirALKarawi/oran-telemetry-elasticity/tree/00314d13784b9e444caca14da063c4786dc09aad/thesis_platform/transport_holdout) · [Execution](https://github.com/YassirALKarawi/oran-telemetry-elasticity/actions/runs/42410102341) · [Raw archive](./verified-42410102341.zip) · [Independent audit](./audit.py)

Archive SHA-256 `794a713392f6c93605cf8065efea711bfbe4e780327c219356bb18808fedc1c2`.
