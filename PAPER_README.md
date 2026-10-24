# Reliability-screened manuscript — 24 October 2026

Current journal revision: IEEE Open Journal of the Communications Society,
using the bundled IEEEoj class. The model includes an exact age-resolved
integer state, delayed-command dynamics, activation-level switching cost,
causal information restriction and necessary deadline-capacity bounds.
`advanced_model.py` adds the formulation; `verify_advanced_model.py` checks it
against six unchanged executions and 306 stage/deadline inequalities.

YASQ revision: see `YASQ_AUDIT.md`. The current build includes a shorter abstract,
additional analytical derivations, a headroom-sensitivity figure and table,
explicit discussion of every visual, nonbreaking tables and a separate conclusion.

Start with `paper_reliability/Manuscript.pdf`. The complete editable manuscript
is `paper_reliability/Manuscript.tex`. The requested author order is Fatima Subhi
Khaleel, Yassir Al-Ameen, and Hamed Al-Raweshidy (corresponding author).
No submission has been made. See `JOURNAL_REVISION.md` for template provenance,
journal sources, revision scope and remaining scientific limitations.

## Executed evidence

- 336 calibration executions on seeds 12000–12005, with two telemetry strata.
- 840 held-out executions: seven settings, six methods, twenty seeds 13000–13019.
- 51 unit-test methods plus historical and current record-level verifiers.
- Independent packet replay, uncached optimizer checks, variable-delay ordering
  checks and six exact full-run replays of current saved results.
- 45 references cited in first-use order, two vector schematics, two unboxed
  algorithms, eight vector result plots, complete seed records and paired tables.

The common reliability target is 0.1% seed-mean misses for each class. Parameter
selection uses one-sided percentile-bootstrap upper endpoints separately in
both calibration strata. This is descriptive screening, not a safety certificate.
The selected headroom is 0.75, fixed expansion is (2,0), and target utilization
is 0.85. No DPP-inspired candidate passes calibration. Its prespecified endpoint
is retained as a clearly labelled diagnostic, not an eligible competitor.

The proposed-versus-fixed comparison qualifies in P, R and J. Mean abstract
incremental-cost reductions are 37.73%, 37.10% and 35.61%, respectively. Markov
traffic, compound batches and constant fifty-slot actuation cause the proposed
policy to fail the absolute risk screen. The compute case has zero proposed
misses but the fixed upper endpoint fails, so it is not counted as a qualified
common-target comparison. No post-test parameter retuning was performed.

## Reproduction

From the extracted `oran_study` directory:

```bash
python -m unittest baseline.simulate experiment evaluate_v3 evaluate_v4 independent_validation verify_extension test_pipeline test_reliability -v
python verify_frozen.py
python verify_extension.py
python verify_paper.py
python verify_reliability.py
python build_reliability_paper.py
python build_submission_figures.py
python scripts/render_repository_figures.py
python build_release.py
```

`requirements.txt` records the Python dependencies used. The build additionally
requires `pdflatex`, the LaTeX packages in the template, and `pdftotext`.
Python 3.12.14 and pdfTeX 1.40.25 were used. `build_reliability_paper.py` checks
resolved references, complete PDF structure and an exact PDF SHA-256 digest.
`build_release.py` retains test receipts and validates every archived file hash.

To rerun test executions, run `python reliability_study.py`. The release omits
the transient `reliability_test_checkpoint.json`, so all held-out settings are
executed again. Calibration data are reused if the protocol hash matches.
To repeat calibration as well, first move `reliability_calibration.json` to a
separate backup location. Do not merge old and newly rerun records.

## Evidence map

| File | Purpose |
|---|---|
| RELIABILITY_PROTOCOL.md | Local design lock, thresholds, seeds, candidate grids and failure rule |
| reliability_calibration.json | All 336 calibration records |
| reliability_selection.json | All candidate scores, eligibility and locked selections |
| reliability_results.json | All 840 held-out records, 42 summaries and 35 paired contrasts |
| reliability_study.py | Workloads, policy adaptations, calibration and evaluation |
| pipeline_control.py | Applied-action/pending-command projection |
| test_reliability.py | Eight new unit-test methods |
| verify_reliability.py | Complete reconciliation and six exact deterministic replays |
| reliability_sections.py | Authored new manuscript sections |
| build_reliability_paper.py | Result-driven tables, plots, manuscript assembly and PDF checks |
| paper_template.tex | Retained historical template, supplying shared model/positioning sections |
| paper_references.py | Shared bibliography with 45 primary-source entries |
| paper_reliability/build_receipt.json | PDF checks, reference count and qualified-result digest |

## Scientific status

This is a complete written synthetic-model study with executed results. It is
not a physical O-RAN implementation, a rare-event reliability certificate, or
a demonstrated state-of-the-art advantage. HPA-inspired and DPP-inspired
comparators are disclosed adaptations rather than faithful system reproductions.
The scientific limitations and directions for physical validation are discussed in the manuscript. `VALIDATION_GATE.md` retains the historical development checklist.
No journal quartile, publication readiness or acceptance is guaranteed.

Historical `paper/`, `paper_results.json`, `PAPER_PROTOCOL.md` and the earlier
technical reports are retained for provenance only. They describe different
experiments and are not the current manuscript or independent additional seeds.

## Repository alignment

`docs/current_study_manifest.json` identifies the current paper and frozen data.
`verify_repository_alignment.py` checks figure order, exact preview pixels, source drawings, navigation, terminology and data hashes.
The current reproduction instructions are in [REPRODUCE.md](REPRODUCE.md).
