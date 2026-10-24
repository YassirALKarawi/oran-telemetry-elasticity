"""Verify the requested journal revision and source layout invariants."""
import re
import json
from pathlib import Path
root=Path(__file__).resolve().parent
t=(root/'paper_reliability/Manuscript.tex').read_text()
assert r'\documentclass{IEEEoj}' in t
results=t.split(r'\section{Results and Mechanistic Interpretation}')[1].split(r'\section{Discussion and Deployment Boundary}')[0]
assert r'\subsection' not in results
assert t.count(r'\hrule\smallskip % journal top rule')==2
algorithm_floats=[m[0] for m in re.finditer(r'\\begin\{figure\*?\}.*?\\end\{figure\*?\}',t,re.S) if r'\textbf{Algorithm' in m[0]]
assert len(algorithm_floats)==2
assert all(r'\begin{figure}[' in x and '[x=1cm,y=1.75cm]' in x for x in algorithm_floats)
for phrase in ['multiple-input multiple-output (MIMO)',r'\boldsymbol{\gamma}(x,\alpha)']:
    assert phrase in t
names=['FATIMA SUBHI KHALEEL','YASSIR AL-AMEEN','HAMED AL-RAWESHIDY']
assert [t.index(n) for n in names]==sorted(t.index(n) for n in names)
assert 'CORRESPONDING AUTHOR: HAMED AL-RAWESHIDY' in t
for label in re.findall(r'\\label\{((?:fig|tab):[^}]+)\}',t):
    assert r'\ref{'+label+'}' in t
for n in [1,2]:assert t.count('Algorithm '+str(n))>=3
for label in ['eq:structuralslack','eq:hopeless','eq:slackbound']:
    assert t.count(r'\label{'+label+'}')==1
assert '2024 author version' not in t
assert '10.1109/TMC.2025.3527707' in t
assert '10.1109/TNET.2023.3275910' in t
assert 'Overfull \\hbox' not in (root/'paper_reliability/Manuscript.log').read_text()
receipt=json.loads((root/'paper_reliability/build_receipt.json').read_text())
assert receipt['pages']<=25
print(json.dumps({'journal':'IEEE OJ-COMS','continuous_results':True,'author_order':names,'top_algorithm_rules':2,'all_visuals_cited':True,'no_horizontal_overflow':True,'pages':receipt['pages']}))
