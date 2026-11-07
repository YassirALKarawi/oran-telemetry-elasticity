# Minimum transport capacity for class 2

The six evaluation loads were separate from the three development loads. All 33 policy/trace combinations started from 50/50, used two non-borrowing Linux token buckets with the same 16 Mbit/s total, and replayed the paired packet schedule across five two-second windows. Each change travelled over the emulated E2 control path. The floor caps the original allocator’s class-1 share after each observation. It guarantees configured bandwidth for class 2, with no guarantee of packet delivery. Linux counters provided out-of-band observations. Measured latency covers application send to application receive on one host.

## Development selection

The development rule considered class-2 floors of 20%, 30% and 40%. Among floors meeting the class-1 retention criterion, the rule maximized mean class-2 on-time delivery. If none qualified, the fallback ranked class-1 and then class-2 on-time delivery. Exact ties favored the smaller floor. The selection JSON was written before evaluation. The reference sets shares proportional to the previous measured offered load. All percentages are equal-weight means of within-trace rates. A missing packet counts as a deadline miss.

| Development variant | Class 1 | Class 2 |
|---|---:|---:|
| floor4 | 44.894% | 55.748% |
| floor6 | 45.757% | 62.896% |
| floor8 | 43.660% | 69.748% |
| proportional | 35.343% | 61.000% |
| thesis | 45.932% | 41.563% |

Selection threshold for class 1: 40.637%. Eligible floors: [20, 30, 40]%. Frozen reservation: 40%.

## Held-out outcomes

| Policy | Class 1 within 15 ms | Class 2 within 40 ms | Both within own deadline |
|---|---:|---:|---:|
| thesis | 54.302% | 41.469% | 47.314% |
| guarded | 50.977% | 65.688% | 57.594% |
| proportional | 45.652% | 58.896% | 51.808% |

| Seed | Method | Class 1 offered / timely / late / missing | Class 2 offered / timely / late / missing |
|---:|---|---|---|
| 971200 | thesis | 9500 / 6974 / 1713 / 813 | 11250 / 4601 / 1135 / 5514 |
| 971200 | guarded | 9500 / 6537 / 1721 / 1242 | 11250 / 7101 / 0 / 4149 |
| 971200 | proportional | 9500 / 6934 / 1707 / 859 | 11250 / 8062 / 0 / 3188 |
| 971201 | thesis | 10250 / 9629 / 0 / 621 | 9250 / 5523 / 387 / 3340 |
| 971201 | guarded | 10250 / 9271 / 0 / 979 | 9250 / 7008 / 0 / 2242 |
| 971201 | proportional | 10250 / 6044 / 2103 / 2103 | 9250 / 6973 / 0 / 2277 |
| 971202 | thesis | 11250 / 1942 / 4602 / 4706 | 7750 / 2526 / 778 / 4446 |
| 971202 | guarded | 11250 / 1983 / 4753 / 4514 | 7750 / 5606 / 0 / 2144 |
| 971202 | proportional | 11250 / 1578 / 3623 / 6049 | 7750 / 2538 / 1150 / 4062 |
| 971203 | thesis | 11000 / 4077 / 3413 / 3510 | 12500 / 4217 / 966 / 7317 |
| 971203 | guarded | 11000 / 4091 / 3591 / 3318 | 12500 / 7293 / 0 / 5207 |
| 971203 | proportional | 11000 / 4032 / 2116 / 4852 | 12500 / 5951 / 0 / 6549 |
| 971204 | thesis | 12500 / 5844 / 3588 / 3068 | 10750 / 4425 / 950 / 5375 |
| 971204 | guarded | 12500 / 4913 / 3590 / 3997 | 10750 / 6932 / 0 / 3818 |
| 971204 | proportional | 12500 / 4254 / 3785 / 4461 | 10750 / 7102 / 0 / 3648 |
| 971205 | thesis | 8750 / 5021 / 1341 / 2388 | 13000 / 5293 / 961 / 6746 |
| 971205 | guarded | 8750 / 4592 / 1341 / 2817 | 13000 / 7811 / 0 / 5189 |
| 971205 | proportional | 8750 / 5009 / 585 / 3156 | 13000 / 7788 / 0 / 5212 |

Original class-1 advantage over proportional: +8.650 pp. Guarded advantage: +5.324 pp. Change for class 2 versus original: +24.219 pp. Prespecified held-out composite criterion: met.

These six short traces cover a single Linux software platform with a custom E2 MAC extension. Results characterize this reservation and baseline on these loads. Independent network-level and physical-radio performance remain untested.

[Frozen protocol](https://github.com/YassirALKarawi/oran-telemetry-elasticity/blob/db744befdfba16086a4db8360b3d8b9495b5bb9e/thesis_platform/reservation/protocol.json) · [Execution](https://github.com/YassirALKarawi/oran-telemetry-elasticity/actions/runs/42412349901) · [Evidence archive](./verified-42412349901.zip) · [Recheck the downloaded archive](./review.py)

Archive SHA-256 `cb305c0e63255b5198b10e40ab5a3d4ddf6ae83047ebeabde1a69ccfbeead67a`.
