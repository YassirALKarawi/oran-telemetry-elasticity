"""Verify authoritative PDF bytes, structure, text references and bibliography."""
import hashlib
import json
import re
from pathlib import Path
import fitz

ROOT=Path(__file__).resolve().parent
P=ROOT/'paper_reliability'
receipt=json.loads((P/'build_receipt.json').read_text())
data=(P/'Manuscript.pdf').read_bytes()
assert data.rstrip().endswith(b'%%EOF')
assert hashlib.sha256(data).hexdigest()==receipt['sha256']
doc=fitz.open(stream=data,filetype='pdf')
assert len(doc)==receipt['pages'] and not doc.is_repaired
text='\n'.join(p.get_text() for p in doc)
assert '[?]' not in text and '??' not in text
assert all(len(p.get_text())>100 for p in doc)
tex=(P/'Manuscript.tex').read_text()
assert tex.count('\\bibitem{')==43
abstract=tex.split('\\begin{abstract}')[1].split('\\end{abstract}')[0]
assert len(abstract.split())<=200
visual_labels=re.findall(r'\\label\{((?:fig|tab):[^}]+)\}',tex)
assert len(visual_labels)==17
assert all('\\ref{'+label+'}' in tex for label in visual_labels)
assert '\\begin{longtable}' not in tex
assert '\\section{Conclusion}' in tex
assert '\\label{eq:ideal}' in tex
body=tex.split('\\begin{thebibliography}')[0]
assert not re.search(r'\bwe\b|\boracle\b',body,re.I)
assert re.findall(r'\\bibitem\{([^}]+)\}',tex)==list(dict.fromkeys(k for c in re.findall(r'\\cite\{([^}]+)\}',tex) for k in c.split(',')))
links=[link['uri'] for p in doc for link in p.get_links() if 'uri' in link]
assert len(links)>=43
assert receipt['qualified_fixed_settings']==['P','R','J']
assert receipt['calibration_runs']==336 and receipt['test_runs']==840
print(json.dumps(dict(pages=len(doc),references=43,external_links=len(links),pdf_sha256=receipt['sha256'],pass_all=True)))
