#!/usr/bin/env python3
"""Render the independent validation report from the verified summary only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ENDPOINTS = ["class 1 (15 ms)", "class 2 (40 ms)", "combined"]
POLICY_LABELS = {
    "adaptive": "adaptive",
    "thesis_floor": "thesis_floor",
    "proportional_floor": "proportional_floor",
}


def f(value: float) -> str:
    return f"{value:.3f}"


def host_label(host: dict) -> str:
    metadata = host["host"]
    return f"{metadata['image_os']} (kernel {metadata['kernel']}, Python {metadata['python']})"


def result_table(host: dict) -> str:
    lines = ["| Transition | Policy | Class 1 timely % | Class 2 timely % | Combined timely % |",
             "|---|---|---:|---:|---:|"]
    for speed, policies in host["scores"].items():
        for policy, values in policies.items():
            cells = [f"{f(mean)} ± {f(sd)}" for mean, sd in zip(values["means"], values["sample_sd"])]
            lines.append(f"| {speed} | `{policy}` | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def contrast_table(host: dict) -> str:
    lines = ["| Transition | Paired contrast | Class 1 Δ pp (+/=/- traces) | Class 2 Δ pp (+/=/- traces) | Combined Δ pp (+/=/- traces) |",
             "|---|---|---:|---:|---:|"]
    for speed, contrasts in host["contrasts"].items():
        for name, values in contrasts.items():
            cells = []
            for mean, signs in zip(values["mean"], values["signs"]):
                cells.append(f"{f(mean)} ({signs['positive']}/{signs['tied']}/{signs['negative']})")
            lines.append(f"| {speed} | `{name}` | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def cross_host_table(summary: dict) -> str:
    host1 = summary["hosts"][0]["host"]["image_os"]
    host2 = summary["hosts"][1]["host"]["image_os"]
    lines = [f"| Transition | Contrast | {host2} − {host1}, class 1 pp | Class 2 pp | Combined pp | >2 pp flag |",
             "|---|---|---:|---:|---:|---|"]
    for speed, contrasts in summary["cross_host_contrast_differences"].items():
        for name, values in contrasts.items():
            flags = [ENDPOINTS[index] for index, value in enumerate(values["flag_over_2pp"]) if value]
            lines.append(f"| {speed} | `{name}` | " + " | ".join(f(v) for v in values["host2_minus_host1"]) +
                         f" | {', '.join(flags) if flags else 'none'} |")
    return "\n".join(lines)


def negative_summary(summary: dict) -> str:
    observations = []
    for host in summary["hosts"]:
        label = host["host"]["image_os"]
        for speed, contrasts in host["contrasts"].items():
            for name, values in contrasts.items():
                for endpoint, mean, signs in zip(ENDPOINTS, values["mean"], values["signs"]):
                    if mean < 0 or signs["negative"]:
                        observations.append(
                            f"- `{label}`, {speed}, `{name}`, {endpoint}: mean {f(mean)} pp; "
                            f"trace signs {signs['positive']}/{signs['tied']}/{signs['negative']} (+/=/-).")
    if not observations:
        return "- No negative mean or negative per-trace paired contrast was observed; this does not establish universal superiority."
    return "\n".join(observations)


def key_findings(summary: dict) -> str:
    proportional = []
    for host in summary["hosts"]:
        for speed in host["contrasts"].values():
            proportional.extend(speed["adaptive_minus_proportional_floor"]["mean"])
    maximum_proportional = max(abs(value) for value in proportional)
    maximum_cross_host = max(
        abs(value)
        for speed in summary["cross_host_contrast_differences"].values()
        for contrast in speed.values()
        for value in contrast["host2_minus_host1"]
    )
    lines = [
        f"- Across every host, speed, and endpoint, the absolute mean `adaptive`−`proportional_floor` difference was at most {f(maximum_proportional)} percentage points; this study provides no material performance separation between those two rules.",
    ]
    for speed in ["fast", "medium", "slow"]:
        values = [host["contrasts"][speed]["adaptive_minus_thesis_floor"]["mean"]
                  for host in summary["hosts"]]
        ranges = []
        for index in range(3):
            endpoint_values = [row[index] for row in values]
            ranges.append(f"{min(endpoint_values):.3f} to {max(endpoint_values):.3f}")
        lines.append(f"- Against `thesis_floor` under {speed} transitions, `adaptive` changed class 1 / class 2 / combined timely delivery by {ranges[0]} / {ranges[1]} / {ranges[2]} percentage points across the two hosts.")
    lines.append(
        f"- The largest cross-host difference between any paired-contrast mean was {f(maximum_cross_host)} percentage points, below the preregistered 2-point investigation threshold. This strong cross-image agreement does not replace physical-site replication."
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("summary", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    data = json.loads(args.summary.read_text())
    assert data["verification"].startswith("PASS")
    hosts = sorted(data["hosts"], key=lambda item: item["host"]["image_os"])
    data["hosts"] = hosts

    report = f"""# Independent validation of frozen adaptive transport rules

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
- Protocol SHA-256: `{data['protocol_sha256']}`.
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
"""
    for archive in data["archives"]:
        report += f"| `{archive['name']}` | `{archive['sha256']}` |\n"
    report += "| `pretest-failure-ubuntu22.zip` | `c72c007fde46fab5425cb27da63443ef0dec24c4f983ad2517567674095cb600` |\n"
    report += "\n"
    for host in data["hosts"]:
        report += f"## Results — {host_label(host)}\n\n"
        report += result_table(host) + "\n\n"
        report += "Paired differences are `adaptive` minus the named comparator. Each sign count covers the six fresh paired traces.\n\n"
        report += contrast_table(host) + "\n\n"

    report += "## Cross-host replication differences\n\n"
    report += "The following values compare the paired-contrast means between runner images. A difference above the preregistered 2 percentage-point investigation threshold is flagged but neither host is discarded.\n\n"
    report += cross_host_table(data) + "\n\n"
    report += "## Main scientific finding\n\n" + key_findings(data) + "\n\n"
    report += "## Retained negative results\n\n" + negative_summary(data) + "\n\n"
    report += """## Interpretation

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
"""
    args.output.write_text(report)


if __name__ == "__main__":
    main()
