# Loss-triggered reservation and repeated transport control

[Frozen protocol and decision rule](https://github.com/YassirALKarawi/oran-telemetry-elasticity/tree/382f530b8886ee2f049c6ebb2981b4a41c2ee471/thesis_platform/adaptive)

A 5% or greater class-2 missing-packet fraction in the last completed window caps the next class-1 share at the proportional baseline. All policies reserve at least 40% for class 2. The trigger and the requirement for all three contrasts to be positive were committed before the experiment. The offered packet counts are sender-side measurements available to this software testbed.

Six new traces were replayed under all three policies, once per trace and policy. Each policy occupied each order position twice. Each replay contained five two-second windows. The budget was 16 Mbit/s and the respective deadlines were 15 and 40 ms. Rates use all sent packets in the denominator.

| Policy | Class 1 timely (%) | Class 2 timely (%) | Combined timely (%) |
|---|---:|---:|---:|
| adaptive | 42.076 | 70.592 | 55.151 |
| thesis_floor | 60.102 | 65.311 | 62.281 |
| proportional_floor | 35.330 | 70.929 | 51.772 |

### Prespecified comparisons

| Adaptive minus reference | Mean paired difference (pp) | Positive / tied / negative traces |
|---|---:|---:|
| Combined vs proportional_floor | +3.378 | 5 / 1 / 0 |
| Class 1 vs proportional_floor | +6.746 | 5 / 1 / 0 |
| Class 2 vs thesis_floor | +5.281 | 6 / 0 / 0 |

Joint criterion: met.

| Trace | Combined adaptive minus proportional (pp) | Class 1 adaptive minus proportional (pp) | Class 2 adaptive minus original guarded thesis (pp) |
|---|---:|---:|---:|
| 1007101 | +9.443 | +18.384 | +2.431 |
| 1007102 | +0.449 | +0.915 | +5.689 |
| 1007103 | +0.063 | +0.110 | +6.982 |
| 1007104 | +0.324 | +0.642 | +6.536 |
| 1007105 | +0.000 | +0.000 | +6.400 |
| 1007106 | +9.991 | +20.427 | +3.651 |

### Repeated OpenFlow meter updates

The separate virtual-switch experiment alternated two offered-load regimes, three measurement windows per block. The applied shares use the preceding window. Host timestamps include the solver, launching and waiting for the xApp, E2 signalling and meter readback. They measure the laboratory implementation end to end. The packet trace and raw meter counters are included.

| Window | Offered 1 / 2 (Mbit/s) | Applied 1 / 2 (Mbit/s) | Received 1 / 2 (Mbit/s) | Decision through readback (s) |
|---:|---|---|---|---:|
| 1 | 17 / 7 | 8.0 / 8.0 | 7.341 / 6.669 | 3.045 |
| 2 | 17 / 7 | 9.6 / 6.4 | 9.238 / 6.169 | 3.045 |
| 3 | 17 / 7 | 9.6 / 6.4 | 9.238 / 6.169 | 3.044 |
| 4 | 7 / 17 | 9.6 / 6.4 | 7.001 / 6.173 | 3.046 |
| 5 | 7 / 17 | 4.8 / 11.2 | 4.633 / 10.774 | 3.052 |
| 6 | 7 / 17 | 4.8 / 11.2 | 4.633 / 10.774 | 3.045 |
| 7 | 17 / 7 | 4.8 / 11.2 | 4.637 / 7.001 | 3.045 |
| 8 | 17 / 7 | 9.6 / 6.4 | 9.238 / 6.165 | 3.045 |
| 9 | 17 / 7 | 9.6 / 6.4 | 9.238 / 6.169 | 3.047 |
| 10 | 7 / 17 | 9.6 / 6.4 | 7.002 / 6.173 | 3.096 |
| 11 | 7 / 17 | 4.8 / 11.2 | 4.633 / 10.774 | 3.045 |
| 12 | 7 / 17 | 4.8 / 11.2 | 4.633 / 10.778 | — |

All 11 issued actions have matching decoded E2 messages and numerical OpenFlow meter readbacks. Median decision-through-readback time was 3.045 s, range 3.044 to 3.096 s. Only the measurement windows carried offered test traffic.

| Constant-load block | Applied class-1 shares (units of 0.8 Mbit/s) | Within-block direction reversals |
|---:|---|---:|
| 1 | [10, 12, 12] | 0 |
| 2 | [12, 6, 6] | 0 |
| 3 | [6, 12, 12] | 0 |
| 4 | [12, 6, 6] | 0 |

Six trace pairs and four short switch blocks support a descriptive comparison on this platform. They do not establish long-run stability, physical radio performance or a general ranking. PRORL rewards are outside this transport comparison. ORANSlice previously demonstrated xApp-based slice prioritization and minimum radio-resource guarantees. A claim of novelty must identify and evaluate a narrower contribution than using E2 control and a minimum share. [ORANSlice, ACM Open AI RAN 2024](https://openrangym.com/ran-frameworks/oranslice)

### Reproduction

- [Run 42417285480](https://github.com/YassirALKarawi/oran-telemetry-elasticity/actions/runs/42417285480) · [42417285480.zip](42417285480.zip) · SHA-256 `2713876a5a07f5c6205c9039476fc57c0867faae7fe52e8d29c8d7675804038a`
- [Run 42417285455](https://github.com/YassirALKarawi/oran-telemetry-elasticity/actions/runs/42417285455) · [42417285455.zip](42417285455.zip) · SHA-256 `e9424df82ea03a22bd016b86cba3ce7167730c81fcbda0dba73101e607e48e52`

Run `python3 verify.py 42417285480.zip 42417285455.zip` to recompute the paired measurements and switch checks. Per-window records include packets that missed their deadlines or never arrived.
