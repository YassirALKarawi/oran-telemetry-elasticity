"""Render GitHub previews from the manuscript's existing vector PDFs."""
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[1]
FIGURES = [
    ('01-architecture', 'submission_figures/Figure_1_Architecture.pdf'),
    ('02-control-timeline', 'submission_figures/Figure_2_Timeline.pdf'),
    ('03-calibration', 'paper_reliability/calibration.pdf'),
    ('04-headroom-sensitivity', 'paper_reliability/headroom_sensitivity.pdf'),
    ('05-reliability-screen', 'paper_reliability/screen_matrix.pdf'),
    ('06-qualified-cost', 'paper_reliability/qualified_cost.pdf'),
    ('07-held-out-results', 'paper_reliability/reliability_primary.pdf'),
    ('08-component-ablations', 'paper_reliability/reliability_ablation.pdf'),
    ('09-cost-components', 'paper_reliability/cost_components.pdf'),
    ('10-proxy-outcome', 'paper_reliability/proxy_vs_outcome.pdf'),
]

def main():
    target = ROOT / 'docs/figures'
    target.mkdir(parents=True, exist_ok=True)
    for name, source in FIGURES:
        with fitz.open(ROOT / source) as doc:
            assert len(doc) == 1, source
            page = doc[0]
            scale = 1600 / page.rect.width
            page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False).save(target / (name + '.png'))
        print(name)

if __name__ == '__main__':
    main()
