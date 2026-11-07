# Local UDP transport actuator check

A controller and a separate user-space forwarder exchanged actual UDP datagrams over Linux IPv4 loopback. Each trial preloaded 700 numbered 128-byte payloads before opening the output gate. The controller measured the two transport queue counts, passed them to the existing thesis allocator, and issued only its transport extra-capacity component. Other stage observations and rate/variance inputs were fixed placeholders. The compute recommendation and class shares were not applied. An explicit reset returned the transport gate to baseline.

Rate mapping for this check was 120 packets/s plus 40 packets/s per transport unit. The allocator requested three units in every trial. The receiver counted arrivals in the central 0.6 seconds of each 0.8-second phase, using a shared host monotonic clock. The queue remained nonempty. No retransmission was needed. Closure accounted for all offered packets as delivered or still buffered.

| Trial | Base packets/s | Controlled packets/s | Reset packets/s | Delivered | Still queued |
|---:|---:|---:|---:|---:|---:|
| 1 | 118.3 | 231.7 | 118.3 | 376 | 324 |
| 2 | 118.3 | 233.3 | 118.3 | 377 | 323 |
| 3 | 118.3 | 231.7 | 116.7 | 375 | 325 |

The experiment measures application-layer forwarding under an imposed output rate on a single host with prefetched traffic. It establishes that the transport decision changed observable receiver throughput under this fixture. It provides no evidence of E2 registration, RIC control, OpenFlow switch reconfiguration, radio performance or SLA improvements. Rate units and measurement windows are engineering choices for this check.

The host returned errno 93 (protocol not supported) on creation of an IPv4 SCTP stream socket. The platform preflight also found no CMake, SWIG, bison, flex or netinet/sctp.h. The next integration milestone requires an SCTP-capable host and the pinned RIC/E2 setup described in the parent directory.

Run python3 thesis_platform/loopback/probe.py from the repository root. observations.json records the issue/observation/acknowledgment timestamps, phase windows and parameters, packet sequence IDs, sizes and receiver timestamps. Wall-clock timing can vary across runs.
