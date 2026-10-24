# Manuscript–repository alignment audit

Checked on 24 October 2026 against the current 22-page manuscript.

## Corrections

- Matched the repository title and reproduction entry points to the current study.
- Expanded two previously undefined abbreviations in the related-work table.
- Separated the candidate-ranking tuple (gamma) from the structural-slack symbol (sigma).
- Removed development-history and document-build commentary from the scientific narrative.
- Preserved scientific limitations, the frozen results, and both single-column algorithms.
- Regenerated all ten figure previews from their source PDFs.

## Verification

`verification_receipt.json` records the executed checks and their outputs. These include 51 unit-test methods, frozen-data validation, numerical and manuscript checks, and `verify_repository_alignment.py`.

The alignment check verifies the manuscript title, 43 cited references, figure order, exact standalone diagram sources, pixel equality of all ten previews, documentation links, the PDF repository hyperlink, and the hashes and counts of the frozen study records. The records contain 336 calibration runs, 840 held-out runs, 42 summaries, and 35 paired comparisons. Reference metadata evidence remains in `reference_metadata_audit.json`.

The rendered 22-page manuscript was visually reviewed for page layout, tables, figures, and single-column algorithms. No overfull horizontal boxes were reported by the manuscript build checks. `SHA256.json` verifies the packaged files.

## Interpretation and scope

These checks support consistency and reproducibility of the supplied synthetic simulation study. They do not establish physical O-RAN validation, rare-event reliability, or journal acceptance. Historical experiments remain separately identified and are not evidence for the current manuscript's numerical claims.

The journal's current policies state that IEEE Open Journal of the Communications Society has no page limit: https://www.comsoc.org/publications/journals/ieee-ojcoms/policies-guidelines
