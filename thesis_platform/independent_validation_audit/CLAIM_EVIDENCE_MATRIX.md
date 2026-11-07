# Claim–evidence matrix for Fatima's thesis transport study

This matrix separates claims established by executable repository evidence from
claims that require a radio testbed or additional scientific work. The independent
validation reported in this directory does not modify the algorithms frozen in
`382f530b8886ee2f049c6ebb2981b4a41c2ee471` and is not evidence for PRORL.

| Candidate claim | Repository evidence | What the evidence establishes | Status / permitted wording | What remains |
|---|---|---|---|---|
| The three frozen rules were evaluated under fast, medium, and slow offered-load transitions. | `independent_protocol.json`, both host ledgers, `verified-summary.json` | The exact same 18 paired traces, deadlines, budget, policy order balancing, and seeds were executed for all three rules. | **Supported for this Linux transport testbed.** State the exact design and report each speed separately. | More traffic families and longer operation are needed for broad or long-run claims. |
| The result repeats across independently allocated Ubuntu 22.04 and 24.04 GitHub-hosted runners. | Two workflow jobs, host manifests, archive hashes, and cross-host contrasts in `RESULTS.md` | Reproducibility across two CI image families for the same protocol and source revision. | **Supported as cross-image CI replication.** | This is not independent hardware/site replication; that requires a separate physical host or laboratory. |
| Control choices were transported through FlexRIC endpoints. | Both hosts: 378 decoded actions and 378 client logs containing `CONTROL ACK rx`; Ubuntu 24.04: post-processed 378 E2 requests and 378 acknowledgements; Ubuntu 22.04: retained raw capture but no `frames.tsv` because the fixed timeout expired | The software endpoints acknowledged every planned action on both hosts; the exact packet-frame gate passed only on Ubuntu 24.04. | **Supported as software FlexRIC endpoint execution, with the capture-gate limitation stated.** Do not describe the cancelled Ubuntu 22.04 workflow as a full pass. | Standard O-RAN interoperability is not established because the experiment uses a patched MAC action extension, not a conformance-tested standard service model. |
| The policies control differentiated transport capacity subject to a common budget. | Linux network namespaces, veth pairs, `tc` TBF state assertions, full packet ledgers | Causal software-testbed behavior under equal 16 Mbit/s shaping and equal timeouts. | **Supported for virtual Linux transport links.** | No direct evidence of PRB scheduling, RF propagation, HARQ, mobility, UE behavior, or a physical gNB. |
| `adaptive` is universally superior to both frozen floors. | Per-trace paired contrasts and retained negative outcomes in `RESULTS.md` | Only the observed direction, magnitude, and variability for each host/speed/endpoint. | **Not a permitted universal claim.** Use descriptive, condition-specific wording; report losses and ties. | A broader preregistered benchmark, formal inference, and competitive modern baselines would be needed. |
| The work is novel relative to prior O-RAN slicing research. | Related-work comparison in `RESULTS.md` | Existing work already demonstrates adaptive xApps, closed-loop slicing, time-varying SLAs, and physical O-RAN testbeds. | **Not established by successful execution.** Any contribution must be framed narrowly around the exact frozen policy and auditable cross-host transport protocol. | A systematic literature review and explicit novelty argument reviewed against the final thesis claims. |
| Current manuscript calibration/evaluation counts and cost reductions are supported by this validation. | `paper_reliability/` artifacts are separate from this directory | Those values belong to the manuscript's synthetic packet-service reliability study, not this transport experiment. | **Do not merge the evidence bases.** | Cite and audit the reliability study separately if those claims remain in the thesis. |
| The approach is ready for operational O-RAN deployment. | No deployment artifact in this study | CI execution proves neither safety nor operational readiness. | **Unsupported.** | Standard E2SM integration, real near-RT RIC/gNB/UE testing, fault injection, security, timing, scalability, and operational monitoring. |
| The policy improves energy efficiency or radio resource utilization. | No energy or physical-radio measurement | No relevant endpoint was measured. | **Unsupported.** | Calibrated power instrumentation and radio-resource telemetry on representative hardware. |
| The study establishes rare-event reliability or long-run stability. | 18 traces × 8 windows per host | A bounded descriptive experiment with fresh seeds and transition-speed strata. | **Unsupported beyond the observed windows.** | Much longer preregistered runs, failure-tail analysis, and appropriate confidence bounds. |

## Hardware-gated verification plan

The following evidence cannot be synthesized in CI. A future hardware stage should
retain the frozen rules and test protocol while replacing the virtual transport
plant with a standards-compatible near-RT RIC, gNB, SDR/RU, core, and multiple UEs.
It should preserve raw E2AP/E2SM captures, KPM inputs, RC/control outputs, PRB
allocations, RF conditions, UE traffic, timing, and calibrated resource/power
measurements. The hardware stage must be treated as a new preregistered experiment,
not as a reason to tune thresholds against the independent results reported here.
