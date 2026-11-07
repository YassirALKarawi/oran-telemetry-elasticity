# Matched reservation comparison and independent virtual-switch test

Eight fresh load traces were frozen before execution. Each of the four policies replayed the same five two-second windows on each trace with a balanced run order. All arms started with equal shares and used a combined allocation of 16 Mbit/s. A 40% floor reserves at least 6.4 Mbit/s for class 2. The denominator for timely delivery includes all sent packets. Rates below average the eight trace-level percentages equally.

| Policy | Class 1 within 15 ms | Class 2 within 40 ms | Combined within deadline |
|---|---:|---:|---:|
| proportional | 43.45% | 55.56% | 49.37% |
| proportional_floor | 40.93% | 68.04% | 54.00% |
| thesis | 45.97% | 37.74% | 42.11% |
| thesis_floor | 42.39% | 64.36% | 52.97% |

### Paired differences in combined timely delivery

| Left arm minus right arm | Mean (pp) | Range across traces (pp) | Positive / tied / negative traces |
|---|---:|---:|---:|
| thesis_floor minus proportional_floor | -1.026 | -3.664 to +1.596 | 5 / 0 / 3 |
| thesis minus proportional | -7.259 | -14.079 to -0.088 | 0 / 0 / 8 |
| thesis_floor minus thesis | +10.857 | -0.945 to +17.705 | 7 / 0 / 1 |
| proportional_floor minus proportional | +4.624 | -2.629 to +12.267 | 6 / 0 / 2 |

Difference between the two floor effects: +6.233 pp. The primary comparison is thesis_floor minus proportional_floor. Per-trace class counts, late arrivals and missing packets are included in factorial-scores.json. All 128 control requests had a corresponding acknowledgement. These eight paired traces are the units of comparison.

### OpenFlow control and receiver measurement

A separate hosted Linux run connected the FlexRIC emulator’s decoded MAC action to a Python controller using ovs-ofctl over loopback TCP with OpenFlow 1.3. Open vSwitch enforced two drop meters on UDP traffic traversing a software bridge. The offered payload rates were 18 and 10 Mbit/s. The decision routine received egress backlog samples at the sender and switch output. These are interface measurements shared by the traffic classes. Each configuration ran three two-second measurements.

| Phase | Meter rates (Mbit/s) | Median receiver rates (Mbit/s) | Switch packets in (class 1 / 2) | Switch drops (class 1 / 2) |
|---|---|---|---|---|
| Before | 8.0 / 8.0 | 7.709 / 7.705 | 13500 / 7500 | 7789 / 1792 |
| After | 9.6 / 6.4 | 9.238 / 6.169 | 13500 / 7500 | 6572 / 2874 |

The packet capture contains one E2 request and acknowledgement, two OpenFlow ADD meter messages and two MODIFY meter messages. Both updated rates agree with the decoded E2 share. The OpenFlow test measures a single transition on a virtual switch. It does not measure physical radio performance, establish general superiority, or test closed-loop stability over repeated transitions. The four-arm deadline comparison used Linux traffic shaping. Its rates should not be pooled with the virtual-switch results or with PRORL utility.

- [Factorial execution](https://github.com/YassirALKarawi/oran-telemetry-elasticity/actions/runs/42415238782) · [Raw evidence](42415238782.zip) · SHA-256 `68731dbb7e3f0d34da29d9a5c5b7dc827d00607bfd003fb6c608618ae87c3f01`
- [OpenFlow execution](https://github.com/YassirALKarawi/oran-telemetry-elasticity/actions/runs/42415861469) · [Raw evidence](42415861469.zip) · SHA-256 `d04c905c7d5b828272c2fb36e2c9b17cd807dc2868f9a58f8313e0b023d94766`

The first SDN attempt stopped during configuration readback before collecting measurements. The next attempt supplied the keyed meter ID but assumed a comma after the printed rate. The successful run checked the same numeric rate using a word boundary. [First setup log](https://github.com/YassirALKarawi/oran-telemetry-elasticity/actions/runs/42415347653) · [Second setup log](https://github.com/YassirALKarawi/oran-telemetry-elasticity/actions/runs/42415602947).

[Independent archive check](audit.py)
