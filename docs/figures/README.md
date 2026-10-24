# Figure gallery

The ten figures below follow the order of the current manuscript. PNG previews are rendered directly from the existing vector PDFs. Click a preview to inspect it, or download the corresponding vector file for publication-quality zoom.

[Repository home](../../README.md) · [Manuscript](../../paper_reliability/Manuscript.pdf) · [Reproduction guide](../../PAPER_README.md)

## Figure 1 · System architecture

![System architecture](01-architecture.png)

Access, transport and compute stages, telemetry reports and the controller's action ledger. Equipment icons describe model roles rather than implemented O-RAN hardware.

[Vector PDF](../../submission_figures/Figure_1_Architecture.pdf) · [Full-resolution PNG](01-architecture.png)

---

## Figure 2 · Observation-to-activation timeline

![Observation-to-activation timeline](02-control-timeline.png)

The causal sequence from delayed reports to command activation. Projection replays only actions already issued.

[Vector PDF](../../submission_figures/Figure_2_Timeline.pdf) · [Full-resolution PNG](02-control-timeline.png)

---

## Figure 3 · Calibration and candidate selection

![Calibration and candidate selection](03-calibration.png)

Candidate cost versus the worst class/stratum upper endpoint. The screening target is 0.1%. Zero empirical endpoints do not certify zero risk.

[Vector PDF](../../paper_reliability/calibration.pdf) · [Full-resolution PNG](03-calibration.png)

---

## Figure 4 · Headroom sensitivity

![Headroom sensitivity](04-headroom-sensitivity.png)

Cost and reliability screening across the frozen headroom grid. Calibration selects among tested candidates.

[Vector PDF](../../paper_reliability/headroom_sensitivity.pdf) · [Full-resolution PNG](04-headroom-sensitivity.png)

---

## Figure 5 · Reliability qualification

![Reliability qualification](05-reliability-screen.png)

The qualification conditions for comparing the proposed policy with fixed capacity, shown separately for every held-out setting.

[Vector PDF](../../paper_reliability/screen_matrix.pdf) · [Full-resolution PNG](05-reliability-screen.png)

---

## Figure 6 · Paired cost differences

![Paired cost differences](06-qualified-cost.png)

Proposed-minus-fixed cost differences. Savings of 35.61–37.73% are qualified only in settings P, R and J.

[Vector PDF](../../paper_reliability/qualified_cost.pdf) · [Full-resolution PNG](06-qualified-cost.png)

---

## Figure 7 · Held-out performance

![Held-out performance](07-held-out-results.png)

Costs and deadline-miss percentages with unadjusted 95% seed-bootstrap intervals. The DPP-inspired adaptation is calibration-ineligible and diagnostic only.

[Vector PDF](../../paper_reliability/reliability_primary.pdf) · [Full-resolution PNG](07-held-out-results.png)

---

## Figure 8 · Component ablations

![Component ablations](08-component-ablations.png)

Action-ledger and headroom ablations on identical test seeds. Error bars quantify seed-mean uncertainty.

[Vector PDF](../../paper_reliability/reliability_ablation.pdf) · [Full-resolution PNG](08-component-ablations.png)

---

## Figure 9 · Cost decomposition

![Cost decomposition](09-cost-components.png)

Capacity and switching contributions computed from the frozen ablation records. Hatched caps indicate switching cost.

[Vector PDF](../../paper_reliability/cost_components.pdf) · [Full-resolution PNG](09-cost-components.png)

---

## Figure 10 · Proxy versus realized outcome

![Proxy versus realized outcome](10-proxy-outcome.png)

Post hoc comparison of surrogate feasibility and observed deadline misses. Surrogate feasibility is not a packet-level reliability guarantee.

[Vector PDF](../../paper_reliability/proxy_vs_outcome.pdf) · [Full-resolution PNG](10-proxy-outcome.png)

---

## Regenerate the previews

From the repository root, with the dependencies in `requirements.txt` installed:

```bash
python scripts/render_repository_figures.py
```

The script changes only the PNG previews. The simulation records and vector source figures remain unchanged.

