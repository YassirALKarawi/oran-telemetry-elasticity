# Reproduce and interpret this artifact

## Current reliability-screened revision, 22 October 2026

Use `PAPER_README.md` for the current commands and evidence map. The authoritative
manuscript is `paper_reliability/Manuscript.pdf`, with 336 calibration and 840
held-out executions and 51 unit-test methods. The material below is a historical
reproduction contract for the preceding technical extension, not the new paper.

## Historical extension scope

This package contains historical pilots plus a verified synthetic service-chain
study. It is not an O-RAN deployment, a calibrated NR simulator, or three completed
journal papers. Start with the new technical report and VALIDATION_GATE.md.
Earlier outputs remain for audit and must not be pooled as independent replications.

## Environment

Python 3.12 was used. Simulation kernels use the standard library. The extension
statistics require NumPy. Report generation uses Matplotlib and a LaTeX engine.
Exact observed Python/NumPy versions are recorded in extension_results.json.
Plots are exported as vector PDFs. Runtime-specific measurements are not claims
about production controller latency.

## Commands, from this directory

```bash
python -m unittest baseline.simulate experiment evaluate_v3 evaluate_v4 independent_validation verify_extension -v
python verify_frozen.py
python verify_extension.py
```

The suite contains 37 unit-test methods, including 18 packet-replay comparisons
and 30 randomly generated independent optimizer comparisons inside two methods.
The frozen-result verifier additionally runs six regression comparisons.

To regenerate the 600 new runs:

```bash
python extension_evaluation.py
python verify_extension.py
python build_professional_report.py
```

The full original frozen evaluation can be regenerated with
`python frozen_evaluation.py`. This reruns 340 calibration and 320 held-out cases.
Default controller behavior remains unchanged after optional ablation arguments
were added. Both the old and new outputs are retained separately.

## Evidence map

| File | Purpose |
|---|---|
| MATHEMATICAL_MODEL.md | Symbols, event order, equations, finite-grid proof and limitations |
| EXTENSION_PROTOCOL.md | Local design lock written before the new seed outcomes |
| extension_results.json | All 600 new run records, summaries, paired intervals and adjusted tests |
| independent_validation.py | Independent packet replay and uncached optimizer implementation |
| verify_extension.py | Accounting and statistical unit tests |
| frozen_results.json | Original calibration and independent evaluation, retained unchanged |
| SOURCE_AUDIT.md | Thirteen focused references with access/claim limits |
| VALIDATION_GATE.md | Remaining requirements before a physical O-RAN or journal-readiness claim |
| professional_report/Research_Study.pdf | Consolidated technical report and numerical analysis |
| professional_report/Research_Study.tex | Editable source with equations and linked bibliography |
| SHA256.json | Integrity hashes, excluding itself, caches, checkpoints and compiler intermediates |

## Interpretation rules

- Miss rates use all measured arrivals, including overdue unfinished packets.
- Twenty independent seed runs, not the total packet count, are the replication units.
- Zero observations do not establish zero failure probability.
- Sign tests test paired direction, not mean equality or noninferiority.
- Resource cost has abstract units and excludes base infrastructure cost.
- Components that fail ablation tests must not be presented as proven improvements.
- Static capacity is preprovisioned. Dynamic capacity has a delayed activation queue.
- Per-decision grid optimality is not global optimal resource allocation.
- All supplied numbers describe the implemented abstraction only.
