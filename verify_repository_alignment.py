"""Check current manuscript, figure previews, repository navigation and data identity."""
import hashlib
import json
import re
from pathlib import Path
from collections import Counter
import fitz
from scripts.render_repository_figures import FIGURES

ROOT=Path(__file__).resolve().parent
tex=(ROOT/'paper_reliability/Manuscript.tex').read_text()
body=tex.split(r'\begin{document}',1)[1].split(r'\begin{thebibliography}',1)[0]
visible=re.sub(r'(?<!\\)%[^\n]*','',body)
for forbidden in [r'\bTODO\b',r'\bTBD\b',r'\bplaceholder\b',r'\breviewer\b',
                  r'\bChatGPT\b',r'\bYASQ\b',r'\bLLM\b',r'hand-entered headline',
                  r'archived study',r'unreported computational benchmark',r'\bvBS\b',r'\brApp\b']:
    assert not re.search(forbidden,visible,re.I),forbidden
assert not re.search(r'\bwe\b|\boracle\b',visible,re.I)
citations=[k for group in re.findall(r'\\cite\{([^}]+)\}',tex) for k in group.split(',')]
assert max(Counter(citations).values())<=3
assert len(set(citations))==43
assert r'\sigma(x,\alpha)' not in tex
assert r'\boldsymbol{\gamma}(x,\alpha)' in tex
assert r'\sigma_{isa}' in tex
title=re.search(r'\\title\{([^}]+)\}',tex)[1].replace('\\','').strip()
assert (ROOT/'README.md').read_text().splitlines()[0]=='# '+title

plot_names=re.findall(r'\\includegraphics\[[^]]*\]\{([^}]+\.pdf)\}',tex)
assert plot_names==[Path(source).name for _,source in FIGURES[2:]]
gallery=(ROOT/'docs/figures/README.md').read_text()
assert len(re.findall(r'^## Figure \d+ ',gallery,re.M))==10
for name,source in FIGURES:
    assert source in gallery and name+'.png' in gallery
    with fitz.open(ROOT/source) as pdf:
        assert len(pdf)==1
        expected=pdf[0].get_pixmap(matrix=fitz.Matrix(1600/pdf[0].rect.width,1600/pdf[0].rect.width),alpha=False)
    actual=fitz.Pixmap(str(ROOT/'docs/figures'/(name+'.png')))
    assert actual.width==expected.width and actual.height==expected.height
    assert actual.samples==expected.samples,name
for label,name in [('fig:architecture','Figure_1_Architecture'),('fig:timeline','Figure_2_Timeline')]:
    block=next(x for x in re.findall(r'\\begin\{figure\*\}.*?\\end\{figure\*\}',tex,re.S) if label in x)
    drawing=re.search(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}',block,re.S)[0]
    assert drawing in (ROOT/'submission_figures'/(name+'.tex')).read_text()
for name in ['README.md','PAPER_README.md','REPRODUCE.md','docs/figures/README.md']:
    path=ROOT/name
    for link in re.findall(r'\]\(([^)]+)\)',path.read_text()):
        if not link.startswith(('https://','http://','#')):
            assert (path.parent/link.split('#')[0]).exists(),(name,link)
with fitz.open(ROOT/'paper_reliability/Manuscript.pdf') as doc:
    links=[link.get('uri') for page in doc for link in page.get_links()]
    assert 'https://github.com/YassirALKarawi/oran-telemetry-elasticity' in links
snapshot=json.loads((ROOT/'docs/current_study_manifest.json').read_text())
for path,digest in snapshot['frozen_data_sha256'].items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
data=json.loads((ROOT/'reliability_results.json').read_text())
assert len(data['runs'])==840 and len(data['summaries'])==42 and len(data['paired'])==35
assert data['calibration_runs']==336 and data['selected']['risk']==.75
print(json.dumps({'figures_matched':10,'pixel_exact_previews':10,'relative_links_valid':True,
                  'editorial_markers_absent':True,'frozen_data_unchanged':True,'passed':True}))
