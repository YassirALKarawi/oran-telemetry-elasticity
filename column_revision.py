"""Column-width algorithms and first-use terminology, without changing steps."""
import re

def finalize_columns(t):
    t=re.sub(r'\\newcommand\{\\algline\}\[3\]\{[^\n]+', lambda m: r'\newcommand{\algline}[3]{\node[anchor=west,align=left,text width=\dimexpr\linewidth-#2cm-25pt\relax,font=\fontsize{8.5}{10}\selectfont,text=black,inner xsep=2pt] at (#2,-.48*#1) {#3};\node[anchor=east,font=\scriptsize\sffamily,text=black!55] at (-.17,-.48*#1) {#1}}',t,count=1)
    def narrow(m):
        s=m[0]
        if r'\textbf{Algorithm' not in s: return s
        return s.replace('figure*','figure').replace('[x=1cm,y=1cm]','[x=1cm,y=1.75cm]').replace(r'\begin{tikzpicture}',r'\noindent\begin{tikzpicture}')
    t=re.sub(r'\\begin\{figure\*\}.*?\\end\{figure\*\}',narrow,t,flags=re.S)
    t=t.replace('cell-free massive MIMO','cell-free massive multiple-input multiple-output (MIMO)')
    t=t.replace('Near-RT latency modeling and RT queue adaptation','Near-real-time latency modeling and real-time queue adaptation')
    t=t.replace('execution JSON','execution records in JavaScript Object Notation (JSON)')
    t=t.replace('The final PDF','The final Portable Document Format (PDF) file')
    t=t.replace("MAREA's delay-aware multi-timescale orchestration",'delay-aware multi-timescale orchestration')
    t=t.replace('COMIX studies interactions between xApps','Conflict management studies interactions between xApps')
    t=t.replace('while OREO orchestrates and shares','while quality-driven intelligence orchestration deploys and shares')
    t=t.replace('SCOPE \\cite{scope}',r'a softwarized prototyping platform \cite{scope}')
    t=t.replace('the 5G-LENA simulator','the fifth-generation (5G) cellular simulator 5G-LENA')
    t=t.replace('external dataset or public archival identifier is asserted.',r'external dataset is used. The code, frozen execution records and reproduction instructions are available at \href{https://github.com/YassirALKarawi/oran-telemetry-elasticity}{github.com/YassirALKarawi/oran-telemetry-elasticity}.')
    return t
