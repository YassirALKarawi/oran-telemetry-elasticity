# KPM subscription and bounded transport actuation

Linux software testbed on a single GitHub-hosted runner. [Run 42407075017](https://github.com/YassirALKarawi/oran-telemetry-elasticity/actions/runs/42407075017) passed on 7 November 2026. FlexRIC revision f56d4487507c7ace392f1ec3f598e7eeda670acc, E2AP v1.01, KPM v3.00.

The per-UE KPM monitor subscribed for eight seconds. Capture frames 22/23 contain the subscription exchange, 31/35/39 contain three indications, and 42/43 contain the subscription deletion. Three callbacks appear in kpm.log. The emulator generates synthetic KPM values, including physically implausible PRB percentages. No performance inference uses these readings.

A separate xApp sent MAC_STATS_V0 action 42 to the emulated gNB. The captured request and acknowledgement appear in frames 59 and 60. The added handler forwards the decoded action through a named pipe to a Linux tc adapter on an isolated veth pair. The E2 acknowledgement confirms the protocol exchange. Queue configuration snapshots and independent receiver measurements verify the transport effect.

| Linux TBF rate (Mbit/s) | Receiver measurements (Mbit/s) | Median (Mbit/s) |
|---|---|---|
| 8 | 7.8252, 7.5416, 7.5387 | 7.5416 |
| 16 | 15.3994, 15.3420, 14.8230 | 15.3420 |

Three sequential iperf3 TCP measurements per phase in the same job. Both xApps exited successfully. This fixed-action actuator test used no learned policy, telemetry-driven decision, external SDN controller, or physical radio.

[Complete original artifact](./verified-42407075017.zip). SHA-256 `bc8e381c0263785347b37375ec613981130a6465c48e8ac8fd1ec23df642d739`. Contains packet capture, decoded frame index, logs, source changes, queue state, and all six receiver reports.

## Prior attempts

[Mixed-style monitoring attempt](./partial-42406364557.zip) recorded traffic and actuation but the monitor exited with status 139. The original CI success flag did not capture that failure. [Interrupted baseline](./partial-42406776173.zip) stopped at the second receiver connection. The verified run used a bounded per-UE subscription, checked both program exits, and started a fresh receiver for each transfer.
