"""Export the original exact vector schematics and graphical abstract."""
import re
import subprocess
from pathlib import Path

root=Path(__file__).resolve().parent
out=root/'submission_figures'
out.mkdir(exist_ok=True)
t=(root/'paper_reliability/Manuscript.tex').read_text()
styles=t[t.index(r'\definecolor{ink}'):t.index(r'\begin{document}')]
figs=re.findall(r'\\begin\{figure\*\}.*?\\end\{figure\*\}',t,re.S)
for label,name in [('fig:architecture','Figure_1_Architecture'),('fig:timeline','Figure_2_Timeline')]:
    fig=next(f for f in figs if '\\label{'+label+'}' in f)
    drawing=fig[fig.index(r'\begin{tikzpicture}'):fig.index(r'\end{tikzpicture}')+len(r'\end{tikzpicture}')]
    source=r'''\documentclass[border=5pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb,tikz,xcolor}
\usetikzlibrary{arrows.meta,positioning,calc}
'''+styles+'\n\\begin{document}\n'+drawing+'\n\\end{document}\n'
    (out/(name+'.tex')).write_text(source)
    result=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',name+'.tex'],cwd=out,capture_output=True,text=True)
    assert result.returncode==0,result.stdout[-2000:]
    if label=='fig:architecture':
        # Journal guidance permits a figure from the article as graphical abstract.
        (out/'Graphical_Abstract.pdf').write_bytes((out/(name+'.pdf')).read_bytes())
print('Exported two vector schematic PDFs and graphical abstract.')
