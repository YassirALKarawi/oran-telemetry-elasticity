# Reproduce the current study

The authoritative paper is [paper_reliability/Manuscript.pdf](paper_reliability/Manuscript.pdf).
Its editable source is [paper_reliability/Manuscript.tex](paper_reliability/Manuscript.tex).
The [figure gallery](docs/figures/README.md) contains the same ten figures.
Historical experiments are retained separately and are not additional replications of this study.

## Environment

Run commands from the repository root. The recorded environment uses Python 3.12,
NumPy 2.3.5, Matplotlib 3.10.8, PyMuPDF 1.26.6 and pdfTeX 1.40.25.
PDF generation also requires `pdftotext` and a LaTeX installation containing
TikZ, standalone, amsmath, amssymb, booktabs and the packages loaded by the sources.
The IEEEoj class is included in `journal_template/`.

```bash
python -m venv .venv
# Activate .venv using the command for your operating system.
python -m pip install -r requirements.txt
```

## Build and verify the saved experiment

```bash
python build_reliability_paper.py
python build_submission_figures.py
python scripts/render_repository_figures.py
python build_release.py
```

The final command runs 51 unit-test methods and the numerical, manuscript and
repository alignment verifiers. It writes `verification_receipt.json`, refreshes
`SHA256.json`, and creates `ORAN_Telemetry_Pilot.zip` in the parent directory.
It checks every file in the ZIP against its SHA-256 entry.

The alignment verifier compares all ten preview images pixel-for-pixel with
fresh renders of the vector figures, checks the two diagram sources against
the manuscript, validates relative documentation links and confirms that the
frozen data hashes match `docs/current_study_manifest.json`.

## Re-execute simulations

```bash
python reliability_study.py
python verify_reliability.py
```

The calibration file is reused when its protocol hash matches. The transient
`reliability_test_checkpoint.json` is omitted from distributed archives, so a
fresh checkout re-executes the 840 held-out runs. To rerun all 336 calibration
runs as well, move `reliability_calibration.json` and any existing
`reliability_test_checkpoint.json` to a separate backup directory before running.
The script writes new selection and result files. Preserve the frozen files
in a separate checkout if comparing execution environments.

The current matrix has seven settings, six methods and twenty test seeds.
`verify_reliability.py` reconciles all 42 summaries and 35 paired contrasts,
then replays six selected complete runs. Runtime metadata can change on a
rerun even when the scientific records agree, so compare run records separately
from whole-file hashes when intentionally regenerating results.

## Evidence boundaries

The 0.1% threshold is a descriptive seed-mean reliability screen. Qualified
cost savings against fixed provisioning occur in P, R and J. Shifted workloads
and long actuation delays include failures. These are synthetic service-chain
results, with no physical O-RAN deployment or rare-event reliability certificate.
