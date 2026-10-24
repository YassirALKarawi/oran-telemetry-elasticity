"""Journal layout and analytical exposition; frozen experiments are untouched."""
import re
import shutil
from journal_equations import wrap_equations

RELATED=r'''\begin{table*}[!t]\centering\small
\caption{Study-level comparison of decision scope and evidence. Positioning studies are not executed benchmarks.}
\label{tab:related}
\begin{tabular}{>{\raggedright\arraybackslash}p{23mm}>{\raggedright\arraybackslash}p{43mm}>{\raggedright\arraybackslash}p{47mm}>{\raggedright\arraybackslash}p{47mm}}
\toprule Study & Controlled object and objective & Timing or uncertainty treatment & Relationship to this experiment\\\midrule
\cite{demir} (2024) & Joint cloud, fronthaul and radio resources with an energy objective & Cross-domain resource coupling in cell-free massive MIMO & Joint allocation is established. The present abstract cost is not measured energy.\\
\cite{oreo} (2025) & Placement and sharing of xApp-based services & Quality-driven orchestration of network intelligence & A different decision object from integer packet-stage capacities.\\
\cite{kalntis} (2025) & Resource thresholds balancing vBS performance and energy & Online learning under changing operating conditions & Formal learning analysis does not transfer to the finite-grid workload heuristic here.\\
\cite{marea} (2025) & Radio-resource allocation for delay-sensitive services & Near-RT latency modeling and RT queue adaptation & A closer delay-aware reference, but radio-resource and violation models differ. No reproduced performance comparison.\\
\cite{kasuluru} (2026) & Multivariate probabilistic resource-demand forecasts & Learned predictive distributions in a containerized rApp & Forecasting richer future demand differs from replaying known commands with held rates.\\
\cite{sora} (2025) & Energy-efficient O-RAN resource allocation & Online learning & Distinguishes learned adaptation from fixed, separately calibrated headroom.\\
\cite{comix} (2025) & Conflict management across xApps & Interactions between control applications & Here, reordering concerns commands from one controller, not competing xApps.\\
\cite{dtc} (2021) & Constrained online network-resource decisions & Delayed feedback and regret analysis & Feedback delay is distinct from immutable, delayed integer activation.\\
\cite{nuberu,concordia} (2021) & Shared vRAN computation and processing deadlines & Implemented processing and scheduling mechanisms & Stronger physical evidence. No equivalence to the synthetic service chain is asserted.\\
\cite{hpa,dppenergy} & Utilization-based sizing and queue-weighted cost & Stabilization or queue-dependent resource decisions & Adapted comparator families executed on the same traces, grids and delays.\\
Present study & Capacity and class shares under a mean-miss screen & Stale reports, issued-command replay and locked headroom & 336 calibration and 840 held-out executions. Conditional savings and failure regimes, without physical validation.\\
\bottomrule\end{tabular}\end{table*}
'''

SLACK=r'''
The age state also gives a sharper necessary deadline condition than queue
length alone. A packet at stage $i$ requires at least $m_i=4-i$ further service
slots because adjacent stages cannot serve it in the same slot. Define its
structural slack and the already-unrecoverable measured workload by
\begin{align}
 \sigma_{isa}(t)&=D_s-a-m_i,\label{eq:structuralslack}\\
 H_s(t)&=\sum_{i=1}^{3}\sum_{a\ge0}\chi(t,a)X_{isa}(t)
            \mathbf1\{\sigma_{isa}(t)<0\}.\label{eq:hopeless}
\end{align}
Even unlimited capacity cannot recover a packet counted by $H_s(t)$ under
the specified event order. Each packet occupies only one stage at that instant.
Consequently, for $N_s>0$,
\begin{equation}
 V_s\ge\frac{\max_{0\le t<T}H_s(t)}{N_s}.
 \label{eq:slackbound}
\end{equation}
The maximum, rather than a sum over time, avoids counting the same packet
repeatedly. This is an original necessary condition derived from the age
recurrences, not an imported stochastic delay guarantee. It is not evaluated
as a new empirical metric because the frozen aggregate records do not retain
every $X_{isa}(t)$. Packet-level service assumptions likewise determine the
applicability of established delay bounds \cite{packetbounds,iwrr}.

The currently issued command has an additional timing restriction. Put
$\omega_{sa}(t)=D_s-a-L_t$. When $\omega_{sa}(t)\le0$, the last permissible
completion slot $t+D_s-a-1$ precedes activation at $t+L_t$. Thus the new
command cannot affect that packet's on-time outcome. Earlier active or pending
commands may still serve it successfully. This command-specific restriction
does not imply that all such packets must miss their deadlines.
'''

ROBUST=r'''
An explicit error margin clarifies what the surrogate would need to guarantee.
For a fixed candidate $(x,\alpha)$, suppose nonnegative demand errors satisfy
$|d^{\star}_{is}-d_{is}|\le b_{is}$, where $d^{\star}_{is}$ denotes a hypothetical
activation-time demand vector. Define
\begin{align}
 B_s(x,\alpha)&=\frac1{\eta D_s}\sum_i
       \frac{b_{is}}{\max(10^{-3},g_{is}(x,\alpha))},\label{eq:robustmargin}\\
 \rho_s^{\star}(x,\alpha)&\le\rho_s(x,\alpha)+B_s(x,\alpha).
 \label{eq:robustscore}
\end{align}
This follows by the triangle inequality applied to the score, holding the
integer allocation fixed. Therefore $\rho_s+B_s\le1$ is sufficient only for
feasibility of that perturbed score. It still does not certify $V_s\le\epsilon$,
because the score omits the age distribution and stage precedence. The executed
controller does not estimate $b_{is}$ or enforce this added condition. These
relations explain the role of an uncertainty budget without claiming a new
robust-control implementation. Delay-aware radio models \cite{marea} and online
resource policies \cite{kalntis} supply different assumptions and guarantees,
which cannot be attached to this heuristic by citation alone.
'''

def journal_revision(t,out,root):
    shutil.copy2(root/'journal_template/IEEEoj.cls',out/'IEEEoj.cls')
    t=t.replace(r'\documentclass[10pt,a4paper]{article}',r'\documentclass{IEEEoj}')
    t=t.replace('lmodern,','').replace(r'\usepackage[margin=21mm]{geometry}','')
    t=t.replace(r'\usepackage{amsmath',r'\let\labelindent\relax'+'\n'+r'\usepackage{amsmath')
    t=t.replace(r'\setlength{\parskip}{3pt}',r'\setlength{\parskip}{0pt}')
    t=t.replace(r'\renewcommand{\topfraction}{0.94}',r'\renewcommand{\topfraction}{0.94}\renewcommand{\dbltopfraction}{0.95}\renewcommand{\dblfloatpagefraction}{0.8}\setcounter{dbltopnumber}{3}')
    t=t.replace(r'\author{}',r'''\author{FATIMA SUBHI KHALEEL\textsuperscript{1}, YASSIR AL-AMEEN\textsuperscript{1}, AND HAMED AL-RAWESHIDY\textsuperscript{2}}
\affil{Department of Communications Engineering, College of Engineering, University of Diyala, Baqubah, Iraq (e-mail: fatima.subhi\_eng@uodiyala.edu.iq).}
\affil{College of Engineering, Design and Physical Sciences, Brunel University of London, Uxbridge, U.K.}
\corresp{CORRESPONDING AUTHOR: HAMED AL-RAWESHIDY (e-mail: hamed.al-raweshidy@brunel.ac.uk).}
\AtBeginDocument{\definecolor{ojcolor}{cmyk}{0.93,0.59,0.15,0.02}}
\def\OJlogo{\parbox{125pt}{\sffamily\bfseries\fontsize{7}{8}\selectfont\color{ojcolor}IEEE OPEN JOURNAL OF THE\\COMMUNICATIONS SOCIETY}}
\markboth{Reliability-Screened Capacity Elasticity}{Khaleel et al.}
% Submission copy: no assigned DOI, volume, acceptance date or copyright claim.
\usepackage{etoolbox}
\makeatletter
\patchcmd{\@maketitle}{\receivedfont}{\receivedfont\iffalse}{}{}
\patchcmd{\@maketitle}{\@editor\fi\par}{\@editor\fi\par\fi}{}{}
\def\ps@submission{\def\@oddhead{\hfill\OJlogo}\let\@evenhead\@oddhead\def\@oddfoot{\hfil\rffont Submission manuscript\hfil\thepage}\let\@evenfoot\@oddfoot}
\makeatother''')
    t=t.replace('\\maketitle\n\\vspace{-12mm}\n','')
    t=t.replace(r'\noindent\textbf{Keywords:}',r'\begin{IEEEkeywords}')
    t=t.replace('telemetry, reliability screening, resource elasticity, reproducible simulation.',
                'telemetry, reliability screening, resource elasticity, reproducible simulation.\n\\end{IEEEkeywords}\n\\maketitle\n\\pagestyle{submission}')
    start=t.index(r'\begin{table}',t.index(r'\section{Related Work'))
    end=t.index(r'\end{table}',start)+len(r'\end{table}')
    t=t[:start]+RELATED+t[end:]
    slack=SLACK.replace('H_s(t)',r'M_s^{\rm irr}(t)').replace('$H_s(t)$',r'$M_s^{\rm irr}(t)$')
    t=t.replace(r'$J,V_s$ &',r'$X_{isa},Y_{isa}$ & Age-resolved queued and served packets\\'+'\n'+r'$m_i,\sigma_{isa},\omega_{sa}$ & Minimum remaining service slots, structural slack and command-relative slack\\'+'\n'+r'$M_s^{\rm irr}$ & Cohort packets already unable to meet their deadline\\'+'\n'+r'$J,V_s$ &')
    t=t.replace(r'\subsection{Telemetry, actuation and switching cost}',slack+'\n'+r'\subsection{Telemetry, actuation and switching cost}')
    a=t.index(r'\section{Results and Mechanistic Interpretation}')
    b=t.index(r'\section{Discussion and Deployment Boundary}',a)
    results=re.sub(r'\\subsection\{[^}]+\}\s*','',t[a:b])
    results=results.replace('The irreversibility property explains',r'For any packet already present at issue, $\omega_{sa}\le0$ because $L>D_s$. Its current command therefore cannot change an on-time completion. The irreversibility property explains')
    results=results.replace('The proxy does not encode packet ages, coupled downstream forecasts or an',r'Equations~\eqref{eq:structuralslack}--\eqref{eq:slackbound} explain why a positive queue-level margin does not reveal recoverable deadline slack. Likewise, \eqref{eq:demanderror}--\eqref{eq:scoreerror} show that a nominal $\rho_s\le1$ leaves demand-error exposure unbudgeted. The proxy does not encode packet ages, coupled downstream forecasts or an')
    t=t[:a]+results+t[b:]
    t=t.replace('\\begin{minipage}{.96\\linewidth}\n', '\\begin{minipage}{.96\\linewidth}\n\\hrule\\smallskip % journal top rule\n')
    # Wide original illustrations, algorithms and detailed tables retain their scale.
    t=t.replace(r'\begin{figure}[',r'\begin{figure*}[').replace(r'\end{figure}',r'\end{figure*}')
    t=t.replace(r'\begin{table}[',r'\begin{table*}[').replace(r'\end{table}',r'\end{table*}')
    t=t.replace('\\begin{table*}[htbp]\\centering\\small\n\\caption{Notation',
                '\\begin{table*}[htbp]\\centering\\footnotesize\\renewcommand{\\arraystretch}{1.04}\n\\caption{Notation')
    t=t.replace(r'\FloatBarrier','')
    # Do not force a new page before every appendix section.
    a=t.index(r'\appendix')
    t=t[:a]+t[a:].replace(r'\begin{table*}',r'\begin{table}').replace(r'\end{table*}',r'\end{table}')
    t=t[:a]+t[a:].replace(r'\centering\footnotesize',r'\centering\fontsize{8}{9}\selectfont\renewcommand{\arraystretch}{1.06}')
    t=t.replace(r'\appendix',r'\onecolumn'+'\n'+r'\appendices')
    t=t.replace(r'\section{Reproduction Contract}',r'\clearpage\twocolumn'+'\n'+r'\section{Reproduction Contract}')
    # Declare the two short diagnostic plots together to avoid a near-empty float page.
    pat=r'\\begin\{figure\*\}.*?\\end\{figure\*\}'
    figures=list(re.finditer(pat,t,re.S))
    comp=next(m[0] for m in figures if 'label{fig:components}' in m[0])
    proxy=next(m[0] for m in figures if 'label{fig:proxyoutcome}' in m[0])
    t=t.replace(proxy,'').replace(comp,comp.replace('width=.98', 'width=.85')+'\n'+proxy.replace('width=.96','width=.85'))
    t=t.replace(r'\pagestyle{submission}',r'\pagestyle{submission}\thispagestyle{submission}\raggedbottom')
    from column_revision import finalize_columns
    return finalize_columns(wrap_equations(t))
