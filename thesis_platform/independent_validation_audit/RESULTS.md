# Independent validation of frozen adaptive transport rules

## Outcome

**Metric and action verification passed on both independently allocated GitHub
runner image families; the full packet-capture frame gate passed on Ubuntu 24.04
and was not reached on Ubuntu 22.04 because the fixed workflow timeout expired.**
The experiment retained the frozen `adaptive`, `thesis_floor`, and
`proportional_floor` rules and did not tune a threshold, floor, deadline, load,
seed, endpoint, or interpretation after observing results. Each host produced
432 measurement windows, 378 decoded control actions, and 378 per-action client
logs containing `CONTROL ACK rx`. Ubuntu 24.04 additionally has the preregistered
post-processed count of 378 captured E2 requests and 378 acknowledgements. The
Ubuntu 22.04 packet capture is preserved, but its `tshark` frame table was not
created before cancellation and is therefore not claimed as a passed gate.

This is descriptive evidence for the specified software transport testbed. It is
not physical O-RAN validation, a standards-conformance result, a rare-event
certificate, or proof of general/state-of-the-art superiority.

## Locked design and execution provenance

- Reference adaptive-audit state: [`25e0a7b395aecbf38f682e2d17c3304d89ea4ccc`](https://github.com/YassirALKarawi/oran-telemetry-elasticity/commit/25e0a7b395aecbf38f682e2d17c3304d89ea4ccc).
- Protocol/code lock before execution: [`69e1ea4277554d3663455ff02192a2770c3edace`](https://github.com/YassirALKarawi/oran-telemetry-elasticity/commit/69e1ea4277554d3663455ff02192a2770c3edace).
- Initial two-host workflow: [`3ab56f7b8b0608243bdf964aef66a984037e049b`](https://github.com/YassirALKarawi/oran-telemetry-elasticity/commit/3ab56f7b8b0608243bdf964aef66a984037e049b), [run 42419357561](https://github.com/YassirALKarawi/oran-telemetry-elasticity/actions/runs/42419357561).
- Ubuntu 22.04 execution-only repair: [`10b87187854898b700b2e6067af073ae40f8a7db`](https://github.com/YassirALKarawi/oran-telemetry-elasticity/commit/10b87187854898b700b2e6067af073ae40f8a7db); single-host retry trigger [`5ac3952f02dd60cbcce6438cd94aa4155407c22c`](https://github.com/YassirALKarawi/oran-telemetry-elasticity/commit/5ac3952f02dd60cbcce6438cd94aa4155407c22c), [run 42419759926](https://github.com/YassirALKarawi/oran-telemetry-elasticity/actions/runs/42419759926).
- Frozen policy source: [`382f530b8886ee2f049c6ebb2981b4a41c2ee471`](https://github.com/YassirALKarawi/oran-telemetry-elasticity/commit/382f530b8886ee2f049c6ebb2981b4a41c2ee471).
- Protocol SHA-256: `a941044a17ec9ec725530370748309b7a8bb469ca579b2c0ae79e43fe9cd9e98`.
- Design: 3 transition speeds × 6 fresh paired traces × 3 policies × 8 two-second windows per host; all six policy orders occur once per speed. Common 16 Mbit/s transport budget, 15/40 ms deadlines, 40% class-2 floor, and identical timeouts.
- Fast, medium, and slow traces change the high-demand class every 1, 2, and 4 windows respectively. The host is a replication stratum, not an extra traffic trace.

The initial Ubuntu 22.04 job stopped before any experiment window because pinned
FlexRIC explicitly rejects GCC 11. The repair installed and selected GCC 12;
scientific code and the locked protocol were unchanged. The retry completed all
432 windows, aggregate scores, 378 decoded actions, 378 ACK-bearing control logs,
and the raw packet capture, then reached the fixed 70-minute timeout before
`tshark` generated `frames.tsv`. This is retained as an evidence-gate failure,
not converted into a workflow success. The completed Ubuntu 24.04 job was not
rerun, and the timeout was not raised after observing the outcome.

## Integrity manifest

| Archive | SHA-256 |
|---|---|
| `independent-validation-ubuntu-22.04.zip` | `53793d288e572b344f0f56e169f011a8559c062e166ff9aed984aefe3eba083d` |
| `independent-validation-ubuntu-24.04.zip` | `abfad9b39b8891a738bd6224001bf1edbca48fbdec039ade3fd3916df611ef4d` |
| `pretest-failure-ubuntu22.zip` | `c72c007fde46fab5425cb27da63443ef0dec24c4f983ad2517567674095cb600` |

## Results — ubuntu22 (kernel 6.8.0-1070-azure, Python 3.10.12)

| Transition | Policy | Class 1 timely % | Class 2 timely % | Combined timely % |
|---|---|---:|---:|---:|
| fast | `adaptive` | 27.610 ± 0.091 | 51.836 ± 0.956 | 39.723 ± 0.433 |
| fast | `thesis_floor` | 27.997 ± 0.055 | 51.836 ± 0.956 | 39.917 ± 0.459 |
| fast | `proportional_floor` | 27.609 ± 0.090 | 51.836 ± 0.956 | 39.723 ± 0.433 |
| medium | `adaptive` | 36.781 ± 5.805 | 66.788 ± 1.787 | 51.869 ± 3.211 |
| medium | `thesis_floor` | 44.886 ± 1.850 | 59.791 ± 1.779 | 52.328 ± 1.287 |
| medium | `proportional_floor` | 36.780 ± 5.806 | 66.788 ± 1.787 | 51.869 ± 3.211 |
| slow | `adaptive` | 42.420 ± 2.915 | 72.421 ± 1.571 | 57.420 ± 1.756 |
| slow | `thesis_floor` | 55.248 ± 1.214 | 61.948 ± 1.571 | 58.598 ± 1.343 |
| slow | `proportional_floor` | 42.420 ± 2.915 | 72.421 ± 1.571 | 57.421 ± 1.756 |

Paired differences are `adaptive` minus the named comparator. Each sign count covers the six fresh paired traces.

| Transition | Paired contrast | Class 1 Δ pp (+/=/- traces) | Class 2 Δ pp (+/=/- traces) | Combined Δ pp (+/=/- traces) |
|---|---|---:|---:|---:|
| fast | `adaptive_minus_proportional_floor` | 0.001 (1/5/0) | 0.000 (0/6/0) | 0.000 (1/5/0) |
| fast | `adaptive_minus_thesis_floor` | -0.387 (0/0/6) | 0.000 (0/6/0) | -0.194 (0/0/6) |
| medium | `adaptive_minus_proportional_floor` | 0.001 (1/5/0) | 0.000 (0/6/0) | 0.000 (1/5/0) |
| medium | `adaptive_minus_thesis_floor` | -8.105 (0/0/6) | 6.996 (6/0/0) | -0.459 (2/0/4) |
| slow | `adaptive_minus_proportional_floor` | -0.001 (0/5/1) | 0.000 (0/6/0) | -0.000 (0/5/1) |
| slow | `adaptive_minus_thesis_floor` | -12.828 (0/0/6) | 10.473 (6/0/0) | -1.178 (0/0/6) |

## Results — ubuntu24 (kernel 7.0.0-1017-azure, Python 3.12.3)

| Transition | Policy | Class 1 timely % | Class 2 timely % | Combined timely % |
|---|---|---:|---:|---:|
| fast | `adaptive` | 27.603 ± 0.083 | 51.836 ± 0.956 | 39.720 ± 0.437 |
| fast | `thesis_floor` | 27.962 ± 0.053 | 51.836 ± 0.956 | 39.899 ± 0.458 |
| fast | `proportional_floor` | 27.602 ± 0.082 | 51.836 ± 0.956 | 39.719 ± 0.437 |
| medium | `adaptive` | 36.773 ± 5.812 | 66.788 ± 1.787 | 51.866 ± 3.214 |
| medium | `thesis_floor` | 44.869 ± 1.852 | 59.791 ± 1.779 | 52.320 ± 1.293 |
| medium | `proportional_floor` | 36.775 ± 5.810 | 66.788 ± 1.787 | 51.866 ± 3.213 |
| slow | `adaptive` | 42.411 ± 2.920 | 72.421 ± 1.571 | 57.416 ± 1.760 |
| slow | `thesis_floor` | 55.230 ± 1.219 | 61.948 ± 1.571 | 58.589 ± 1.347 |
| slow | `proportional_floor` | 42.414 ± 2.918 | 72.421 ± 1.571 | 57.417 ± 1.759 |

Paired differences are `adaptive` minus the named comparator. Each sign count covers the six fresh paired traces.

| Transition | Paired contrast | Class 1 Δ pp (+/=/- traces) | Class 2 Δ pp (+/=/- traces) | Combined Δ pp (+/=/- traces) |
|---|---|---:|---:|---:|
| fast | `adaptive_minus_proportional_floor` | 0.001 (2/3/1) | 0.000 (0/6/0) | 0.000 (2/3/1) |
| fast | `adaptive_minus_thesis_floor` | -0.359 (0/0/6) | 0.000 (0/6/0) | -0.180 (0/0/6) |
| medium | `adaptive_minus_proportional_floor` | -0.002 (0/4/2) | 0.001 (1/5/0) | -0.000 (1/3/2) |
| medium | `adaptive_minus_thesis_floor` | -8.096 (0/0/6) | 6.997 (6/0/0) | -0.454 (2/0/4) |
| slow | `adaptive_minus_proportional_floor` | -0.002 (0/3/3) | 0.000 (0/6/0) | -0.001 (0/3/3) |
| slow | `adaptive_minus_thesis_floor` | -12.819 (0/0/6) | 10.473 (6/0/0) | -1.173 (0/0/6) |

## Cross-host replication differences

The following values compare the paired-contrast means between runner images. A difference above the preregistered 2 percentage-point investigation threshold is flagged but neither host is discarded.

| Transition | Contrast | ubuntu24 − ubuntu22, class 1 pp | Class 2 pp | Combined pp | >2 pp flag |
|---|---|---:|---:|---:|---|
| fast | `adaptive_minus_proportional_floor` | 0.000 | 0.000 | -0.000 | none |
| fast | `adaptive_minus_thesis_floor` | 0.028 | 0.000 | 0.014 | none |
| medium | `adaptive_minus_proportional_floor` | -0.002 | 0.001 | -0.001 | none |
| medium | `adaptive_minus_thesis_floor` | 0.010 | 0.001 | 0.005 | none |
| slow | `adaptive_minus_proportional_floor` | -0.002 | 0.000 | -0.001 | none |
| slow | `adaptive_minus_thesis_floor` | 0.009 | 0.000 | 0.005 | none |

## Main scientific finding

- Across every host, speed, and endpoint, the absolute mean `adaptive`−`proportional_floor` difference was at most 0.002 percentage points; this study provides no material performance separation between those two rules.
- Against `thesis_floor` under fast transitions, `adaptive` changed class 1 / class 2 / combined timely delivery by -0.387 to -0.359 / 0.000 to 0.000 / -0.194 to -0.180 percentage points across the two hosts.
- Against `thesis_floor` under medium transitions, `adaptive` changed class 1 / class 2 / combined timely delivery by -8.105 to -8.096 / 6.996 to 6.997 / -0.459 to -0.454 percentage points across the two hosts.
- Against `thesis_floor` under slow transitions, `adaptive` changed class 1 / class 2 / combined timely delivery by -12.828 to -12.819 / 10.473 to 10.473 / -1.178 to -1.173 percentage points across the two hosts.
- The largest cross-host difference between any paired-contrast mean was 0.028 percentage points, below the preregistered 2-point investigation threshold. This strong cross-image agreement does not replace physical-site replication.

## Retained negative results

- `ubuntu22`, fast, `adaptive_minus_thesis_floor`, class 1 (15 ms): mean -0.387 pp; trace signs 0/0/6 (+/=/-).
- `ubuntu22`, fast, `adaptive_minus_thesis_floor`, combined: mean -0.194 pp; trace signs 0/0/6 (+/=/-).
- `ubuntu22`, medium, `adaptive_minus_thesis_floor`, class 1 (15 ms): mean -8.105 pp; trace signs 0/0/6 (+/=/-).
- `ubuntu22`, medium, `adaptive_minus_thesis_floor`, combined: mean -0.459 pp; trace signs 2/0/4 (+/=/-).
- `ubuntu22`, slow, `adaptive_minus_proportional_floor`, class 1 (15 ms): mean -0.001 pp; trace signs 0/5/1 (+/=/-).
- `ubuntu22`, slow, `adaptive_minus_proportional_floor`, combined: mean -0.000 pp; trace signs 0/5/1 (+/=/-).
- `ubuntu22`, slow, `adaptive_minus_thesis_floor`, class 1 (15 ms): mean -12.828 pp; trace signs 0/0/6 (+/=/-).
- `ubuntu22`, slow, `adaptive_minus_thesis_floor`, combined: mean -1.178 pp; trace signs 0/0/6 (+/=/-).
- `ubuntu24`, fast, `adaptive_minus_proportional_floor`, class 1 (15 ms): mean 0.001 pp; trace signs 2/3/1 (+/=/-).
- `ubuntu24`, fast, `adaptive_minus_proportional_floor`, combined: mean 0.000 pp; trace signs 2/3/1 (+/=/-).
- `ubuntu24`, fast, `adaptive_minus_thesis_floor`, class 1 (15 ms): mean -0.359 pp; trace signs 0/0/6 (+/=/-).
- `ubuntu24`, fast, `adaptive_minus_thesis_floor`, combined: mean -0.180 pp; trace signs 0/0/6 (+/=/-).
- `ubuntu24`, medium, `adaptive_minus_proportional_floor`, class 1 (15 ms): mean -0.002 pp; trace signs 0/4/2 (+/=/-).
- `ubuntu24`, medium, `adaptive_minus_proportional_floor`, combined: mean -0.000 pp; trace signs 1/3/2 (+/=/-).
- `ubuntu24`, medium, `adaptive_minus_thesis_floor`, class 1 (15 ms): mean -8.096 pp; trace signs 0/0/6 (+/=/-).
- `ubuntu24`, medium, `adaptive_minus_thesis_floor`, combined: mean -0.454 pp; trace signs 2/0/4 (+/=/-).
- `ubuntu24`, slow, `adaptive_minus_proportional_floor`, class 1 (15 ms): mean -0.002 pp; trace signs 0/3/3 (+/=/-).
- `ubuntu24`, slow, `adaptive_minus_proportional_floor`, combined: mean -0.001 pp; trace signs 0/3/3 (+/=/-).
- `ubuntu24`, slow, `adaptive_minus_thesis_floor`, class 1 (15 ms): mean -12.819 pp; trace signs 0/0/6 (+/=/-).
- `ubuntu24`, slow, `adaptive_minus_thesis_floor`, combined: mean -1.173 pp; trace signs 0/0/6 (+/=/-).

## Interpretation

The correct interpretation is conditional: the tables quantify how each frozen
rule behaved for each transition speed and host image. Aggregate combined timely
delivery must not conceal class-specific losses, and a favorable mean must not
erase negative paired traces. The two hosts share the same GitHub infrastructure
provider and therefore do not constitute physical-site replication.

## Manuscript-claim audit

The current manuscript's 336 calibration runs, 840 held-out runs, and reported
35.61–37.73% abstract incremental-cost reductions belong to the separate
synthetic packet-service reliability study under `paper_reliability/`. They are
not additional samples for this transport validation and must not be pooled with
its percentages. The manuscript already describes those conclusions as
conditional within a synthetic model and explicitly excludes physical O-RAN
validation and rare-event certification; those boundaries remain correct.

The present study can support a narrower statement: three already-frozen rules
were executed on paired dynamic transport traces on two CI image families, with
complete per-window ledgers and ACK-bearing control logs on both, plus the full
packet-frame gate on Ubuntu 24.04. It cannot turn abstract
service units into PRBs, CPU cycles, RF performance, energy, or operational SLA
guarantees. See `CLAIM_EVIDENCE_MATRIX.md` for claim-by-claim wording.

## Prior-work comparison and novelty boundary

| Prior work | Relevant existing evidence | Boundary for this thesis |
|---|---|---|
| O-RAN-enabled intelligent slicing for SLA, IEEE TMC 2025, [DOI/record](https://ieeexplore.ieee.org/document/10721269/) | Two-level DRL scheduling evaluated in a simulator and an O-RAN-compliant testbed | Adaptive slicing and physical O-RAN testbed validation already exist; neither is novel merely because this workflow succeeds. |
| DRL slicing with time-varying SLAs, ICNC 2024, [DOI](https://doi.org/10.1109/ICNC59896.2024.10556357) | Dynamic SLA adaptation in OpenRAN Gym without retraining | Varying requirements and adaptation are established; the present rules and transport-only evidence are narrower. |
| Near-real-time VR traffic control in O-RAN, 2024, [preprint](https://arxiv.org/abs/2401.01652) | Experimental xApp follows load variation and controls latency/resource allocation | Dynamic load-following in an O-RAN testbed is prior evidence; this CI study does not reproduce its physical setting. |
| xSlice, IEEE Transactions on Networking 2025, [DOI](https://doi.org/10.1109/TON.2025.3628209) | Online-learning xApp evaluated with ten smartphones | Modern physical and learning baselines are stronger deployment evidence than virtual `tc` links. |
| LACO, IEEE TWC 2021, [DOI](https://doi.org/10.1109/TWC.2020.3027963) | Latency/throughput-aware slicing with off-the-shelf experimental equipment | Adaptive orchestration and experimental validation predate this work; novelty must rest on a precisely delimited auditable mechanism, not the broad objective. |

These works were not reproduced as numerical baselines, so their published
metrics are not directly compared with this experiment's timely-delivery rates.
At most, the new contribution can be framed as an auditable, preregistered
cross-image transport validation of a specific frozen heuristic, with explicit
negative results and evidence-chain verification.

## What requires hardware

CI proves source execution, Linux traffic shaping, packet timing in the virtual
plant, and end-to-end passage of the patched FlexRIC MAC control message. A
standards-compatible gNB/RU or SDR, core, multiple UEs, and a near-RT RIC are
required to test E2SM-KPM inputs, E2SM-RC or another standard control path, PRB
scheduling, radio-channel variation, mobility, HARQ, CPU timing, isolation,
power, and actual end-to-end latency. Such a stage must be separately
preregistered and may not retune the rule using these independent results.

## Verification procedure

`verify_independent.py` extracts both archives, checks the protocol identity and
hash, recomputes every frozen decision from completed observations, reconstructs
every timely/late/missing count, recomputes all means and sample standard
deviations, checks action chronology, verifies the pinned FlexRIC revision, and
requires 378 ACK-bearing per-action logs per host. It additionally requires the
exact 378/378 packet-capture request/acknowledgement counts where `frames.tsv`
exists, and explicitly marks Ubuntu 22.04 as `NOT_RUN_WORKFLOW_TIMEOUT` rather
than inferring a passed capture gate. The report is rendered only from its
machine-readable `verified-summary.json` output.

No PRORL training was started or rerun, no test-data retuning occurred, and no
journal submission was made.
