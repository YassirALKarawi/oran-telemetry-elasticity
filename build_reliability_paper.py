"""Generate the reliability revision from executed records, then verify PDF refs."""
import json
import re
import subprocess
import hashlib
import os
import tempfile
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from paper_references import REFS
from reliability_sections import (FRONT,RELATED_ADDITION,CALIBRATION_AND_BASELINES,
                                  IRREVERSIBILITY,METHODS,RESULTS,DISCUSSION)
from reliability_study import EPS,DELTA
from yasq_revision import revise,unsplit
from yasq_quality import refine
from substantive_revision import rebuild
from advanced_model import enrich
from editorial_polish import polish, install_plot_style
from realistic_schematics import replace_schematics
from journal_revision import journal_revision
install_plot_style()

ROOT=Path(__file__).resolve().parent
FINAL=ROOT/'paper_reliability'
FINAL.mkdir(exist_ok=True)
# Keep every compiler pass private. Publish only closed, validated final files.
OUT=Path(tempfile.mkdtemp(prefix='reliability-build-',dir=ROOT.parent))
D=json.loads((ROOT/'reliability_results.json').read_text())
S=json.loads((ROOT/'reliability_selection.json').read_text())
CASES=list(dict.fromkeys(r['case'] for r in D['summaries']))
SHORT=dict(zip(CASES,['P','M','B','C','R','L','J']))
ORDER=['risk','fixed','hpa','dpp','uncalibrated','no_ledger']
NAMES={'risk':'Proposed','fixed':'Fixed','hpa':'HPA-inspired','dpp':'DPP-inspired',
       'uncalibrated':'Uncalibrated','no_ledger':'No ledger'}
COLORS={'risk':'#14785e','fixed':'#354359','hpa':'#bc6430','dpp':'#9566a5',
        'uncalibrated':'#b64447','no_ledger':'#2784a7'}
MARKERS=dict(zip(ORDER,['o','s','^','D','v','X']))

def row(c,m): return next(r for r in D['summaries'] if r['case']==c and r['method']==m)
def paired(c,m): return next(r for r in D['paired'] if r['case']==c and r['comparator']==m)
def qualifies(c,m='fixed'):
    return (D['selected']['risk'] is not None and D['selected'].get(m) is not None
            and max(row(c,'risk')['upper95'])<=EPS and max(row(c,m)['upper95'])<=EPS
            and max(paired(c,m)['miss_upper95'])<=DELTA and paired(c,m)['cost_ci'][1]<0)
def pct(v): return f'{100*v:.4f}'
def pairpct(v): return '('+', '.join(pct(x) for x in v)+')'
def costci(p): return f'{p["cost_difference"]:.1f} [{p["cost_ci"][0]:.1f}, {p["cost_ci"][1]:.1f}]'
def savings(c): return 100*(1-row(c,'risk')['cost']/row(c,'fixed')['cost'])

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,
                     'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,
                     'grid.alpha':.18,'legend.frameon':False})
fig,ax=plt.subplots(figsize=(8.4,3.9))
for m in ['fixed','risk','hpa','dpp']:
    rr=[r for r in S['scores'] if r['method']==m]
    x=[r['cost'] for r in rr]
    y=[max(1e-4,100*max(v for s in r['strata'] for v in s['upper95'])) for r in rr]
    ax.scatter(x,y,c=COLORS[m],marker=MARKERS[m],s=44,label=NAMES[m],alpha=.85)
    if m=='risk':
        for a,b,r in zip(x,y,rr): ax.annotate('eta='+str(r['param']),(a,b),xytext=(5,7),textcoords='offset points',fontsize=8)
ax.axhline(.1,color='#555555',ls='--',lw=1,label='0.1% screen')
ax.set_yscale('log');ax.set_ylim(5e-5,100)
ax.set_xlabel('Mean incremental calibration cost')
ax.set_ylabel('Worst upper endpoint (%)')
ax.legend(ncol=3,fontsize=8,loc='upper right')
fig.tight_layout();fig.savefig(OUT/'calibration.pdf');plt.close(fig)

def draw_summary(filename,methods,figsize):
    fig,axes=plt.subplots(3,1,figsize=figsize,sharex=True)
    for j,m in enumerate(methods):
        rr=[row(c,m) for c in CASES]; x=np.arange(len(CASES))+(j-(len(methods)-1)/2)*.13
        for k,ax in enumerate(axes):
            y=np.array([r['cost'] if k==0 else 100*r['violation'][k-1] for r in rr])
            ci=np.array([r['cost_ci'] if k==0 else [100*v for v in r['ci'][k-1]] for r in rr])
            ax.errorbar(x,y,yerr=np.maximum(0,[y-ci[:,0],ci[:,1]-y]),fmt=MARKERS[m],
                        color=COLORS[m],capsize=2,ms=4.5,lw=1,label=NAMES[m])
    axes[0].legend(ncol=len(methods),fontsize=8,loc='upper center',bbox_to_anchor=(.5,1.18))
    axes[0].set_ylabel('Incremental cost');axes[0].set_ylim(bottom=0)
    for s,ax in enumerate(axes[1:]):
        ax.axhline(.1,color='#555555',ls='--',lw=.9)
        ax.set_yscale('symlog',linthresh=.1,linscale=.8)
        ax.set_yticks([0,.1,1,10]);ax.set_yticklabels(['0','0.1','1','10'])
        ax.set_ylim(bottom=-.015)
        ax.set_ylabel(f'Class {s} misses (%)')
    axes[-1].set_xticks(range(len(CASES)),[SHORT[c] for c in CASES])
    axes[-1].set_xlabel('Held-out setting (linear below 0.1%, logarithmic above)')
    fig.tight_layout();fig.savefig(OUT/filename);plt.close(fig)

draw_summary('reliability_primary.pdf',['risk','fixed','hpa','dpp'],(8.7,6.5))
draw_summary('reliability_ablation.pdf',['risk','uncalibrated','no_ledger'],(8.7,5.9))
fig,ax=plt.subplots(figsize=(8.3,3.4))
for j,c in enumerate(CASES):
    p=paired(c,'fixed');mean=p['cost_difference'];lo,hi=p['cost_ci']
    ax.errorbar(mean,j,xerr=[[mean-lo],[hi-mean]],fmt='o',capsize=3,
                color='#14785e' if qualifies(c) else '#7c8188',ms=6)
    ax.annotate('qualified' if qualifies(c) else 'unqualified',(hi,j),xytext=(8,0),
                textcoords='offset points',va='center',fontsize=8)
ax.axvline(0,color='gray',lw=1);ax.set_yticks(range(7),[SHORT[c] for c in CASES]);ax.invert_yaxis()
ax.set_xlim(-3100,100);ax.set_xlabel('Paired incremental-cost difference (proposed minus fixed)')
fig.tight_layout();fig.savefig(OUT/'qualified_cost.pdf');plt.close(fig)

qualified=[c for c in CASES if qualifies(c)]
assert qualified, 'Manuscript narrative requires at least one qualified comparison'
qrange=f'{min(savings(c) for c in qualified):.2f}--{max(savings(c) for c in qualified):.2f}'
qnames=', '.join(SHORT[c] for c in qualified)
qt=[r'\begin{table}[htbp]\centering\footnotesize',
    r'\caption{Common-target comparison against fixed capacity. Upper endpoints are percentages. Cost intervals are paired, unadjusted 95\% intervals.}',
    r'\begin{tabular}{lccrl}\toprule Setting & Proposed $(U_0,U_1)$ & Fixed $(U_0,U_1)$ & $\Delta J$ [95\% interval] & Qualified\\\midrule']
for c in CASES:
    qt.append(f'{SHORT[c]} & {pairpct(row(c,"risk")["upper95"])} & {pairpct(row(c,"fixed")["upper95"])} & {costci(paired(c,"fixed"))} & {"Yes" if qualifies(c) else "No"} \\\\')
qt.extend([r'\bottomrule\end{tabular}\label{tab:qualified}',r'\end{table}'])

ft=[r'\small\begin{longtable}{llrrrrr}',
    r'\caption{Complete test results, twenty seeds per row. Miss fractions and one-sided upper endpoints are percentages. DPP-inspired results are diagnostic after calibration failure.}\\',
    r'\toprule Setting & Method & Mean $V_0$ & Mean $V_1$ & Upper $V_0$ & Upper $V_1$ & Mean cost\\\midrule\endfirsthead',
    r'\toprule Setting & Method & Mean $V_0$ & Mean $V_1$ & Upper $V_0$ & Upper $V_1$ & Mean cost\\\midrule\endhead',r'\bottomrule\endfoot']
for c in CASES:
    for m in ORDER:
        r=row(c,m)
        ft.append(f'{SHORT[c]} & {NAMES[m]} & {pct(r["violation"][0])} & {pct(r["violation"][1])} & {pct(r["upper95"][0])} & {pct(r["upper95"][1])} & {r["cost"]:.2f} \\\\')
    ft.append(r'\addlinespace')
ft.extend([r'\end{longtable}\normalsize'])
pt=[r'\footnotesize\begin{longtable}{llrcc}',
    r'\caption{All paired contrasts, proposed minus comparator. Miss differences and upper endpoints are percentage points. No multiplicity-adjusted claim is made.}\\',
    r'\toprule Setting & Comparator & $\Delta J$ [95\% interval] & Mean $(\Delta V_0,\Delta V_1)$ & Upper $(\Delta V_0,\Delta V_1)$\\\midrule\endfirsthead',
    r'\toprule Setting & Comparator & $\Delta J$ [95\% interval] & Mean $(\Delta V_0,\Delta V_1)$ & Upper $(\Delta V_0,\Delta V_1)$\\\midrule\endhead',r'\bottomrule\endfoot']
for c in CASES:
    for m in ORDER[1:]:
        p=paired(c,m)
        pt.append(f'{SHORT[c]} & {NAMES[m]} & {costci(p)} & {pairpct(p["miss_difference"])} & {pairpct(p["miss_upper95"])} \\\\')
    pt.append(r'\addlinespace')
pt.extend([r'\end{longtable}\normalsize'])

cal='The selected fixed expansion is $(x_2,x_3)=(2,0)$, the selected headroom is $\\eta=0.75$, and the selected utilization is $u=0.85$. '
cal+='No DPP-inspired candidate passes both calibration strata, so price $v=0.1$ is retained only as the prespecified diagnostic endpoint. '
cal+='The $\\eta=1$ controller fails calibration. The three lower headroom candidates pass, and $0.75$ has the lowest calibration cost among them. '
cal+='Figure~\\ref{fig:calibration} shows every candidate, including unsuccessful ones. Passing the empirical screen does not imply a confidence-certified feasible set.'
primary=f'The complete qualification rule passes in {len(qualified)} of seven fixed-reference comparisons: {qnames}. Mean incremental-cost reductions in those settings range from {qrange}\\%. '
for c in qualified:
    r=row(c,'risk');p=paired(c,'fixed')
    primary+=f'In {SHORT[c]}, proposed cost is {r["cost"]:.2f} versus {row(c,"fixed")["cost"]:.2f}, a reduction of {savings(c):.2f}\\%, with paired cost difference {costci(p)}. '
primary+='These are common-threshold comparisons, not proof that the policies have identical reliability. In C, the proposed policy has zero observed misses, but the fixed class-1 upper endpoint exceeds the target, so that cost reduction is not counted as a qualified comparison.'
shift='The proposed classwise mean miss percentages are '
shift+=', '.join(f'{pairpct(row(c,"risk")["violation"])} in {SHORT[c]}' for c in [CASES[1],CASES[2],CASES[5]])+'. '
shift+='The corresponding upper endpoints fail the target in all three settings. '
shift+=f'At constant $L=50$, class-1 misses reach {pct(row(CASES[5],"risk")["violation"][1])}\\%, while the fixed mean is {pct(row(CASES[5],"fixed")["violation"][1])}\\%. '
shift+='The jitter case J passes the descriptive screen, but this does not contradict the long-delay failure: its mixture contains many shorter activations and its mean is below fifty slots. '
shift+='The HPA-inspired family also fails some fresh-seed screens despite passing calibration. The DPP-inspired family has already failed calibration and is never counted as an eligible cost comparator.'
c=CASES[0];a=row(c,'risk');b=row(c,'no_ledger');u=row(c,'uncalibrated')
ablation=f'In P, no-ledger cost is {b["cost"]:.2f} versus {a["cost"]:.2f} for the proposed controller, a {100*(1-a["cost"]/b["cost"]):.2f}\\% reduction from adding the ledger at the selected headroom. Both have zero observed misses in this setting. '
ablation+=f'Without calibrated headroom, cost falls to {u["cost"]:.2f}, but mean class-0 and class-1 misses become {pct(u["violation"][0])}\\% and {pct(u["violation"][1])}\\%. '
ablation+='Thus a lower raw cost can reverse the intended interpretation when reliability is omitted. Appendix B reports all paired ablation differences, including the cases where the ledger does not improve a deadline endpoint.'

headroom=sorted([r for r in S['scores'] if r['method']=='risk'],key=lambda r:r['param'])
fig,axs=plt.subplots(1,2,figsize=(8.5,3.1))
eta=[r['param'] for r in headroom]
axs[0].plot(eta,[r['cost'] for r in headroom],'-o',color=COLORS['risk'],lw=1.5)
axs[0].set_ylabel('Mean calibration cost')
for s in (0,1):
    vals=[100*max(st['upper95'][s] for st in r['strata']) for r in headroom]
    axs[1].plot(eta,vals,marker=['o','s'][s],color=[COLORS['risk'],COLORS['fixed']][s],label=f'Class {s}')
axs[1].axhline(.1,color='gray',ls='--',lw=1,label='0.1% target')
axs[1].set_ylabel('Worst-stratum upper endpoint (%)');axs[1].legend(fontsize=8)
for ax in axs: ax.set_xlabel('Headroom parameter eta');ax.set_xticks(eta)
fig.tight_layout();fig.savefig(OUT/'headroom_sensitivity.pdf');plt.close(fig)
sens=[r'\subsection{Sensitivity to calibrated headroom}',
      r'Figure~\ref{fig:headroom} and Table~\ref{tab:headroom} report the complete predeclared headroom sweep. Each point uses the same twelve calibration runs across two report strata. The plotted upper endpoint is the worse of the two strata for the indicated class.',
      r'\begin{table}[htbp]\centering\small',
      r'\caption{Headroom sensitivity on calibration seeds. Upper endpoints are percentages.}\label{tab:headroom}',
      r'\begin{tabular}{rrrrl}\toprule $\eta$ & Mean cost & Upper $V_0$ & Upper $V_1$ & Eligible\\\midrule']
for r in headroom:
    vv=[100*max(st['upper95'][s] for st in r['strata']) for s in (0,1)]
    sens.append(f'{r["param"]:.2f} & {r["cost"]:.2f} & {vv[0]:.4f} & {vv[1]:.4f} & {"Yes" if r["eligible"] else "No"} \\\\')
sens.extend([r'\bottomrule\end{tabular}\end{table}',
    r'\begin{figure}[htbp]\centering\includegraphics[width=.96\linewidth]{headroom_sensitivity.pdf}',
    r'\caption{Sensitivity to headroom on the frozen calibration grid. Left: mean incremental cost. Right: worst-stratum classwise upper endpoints. The dashed line marks the empirical screening target.}\label{fig:headroom}\end{figure}',
    r'The observed cost increase as $\eta$ decreases is consistent with the nested feasible sets in \eqref{eq:feasibleset}. Values $0.25$ and $0.50$ incur substantially greater cost than $0.75$, although all three have zero empirical miss endpoints on these calibration seeds. The value $1.00$ admits cheaper decisions but fails the target. This comparison supports the selected grid point for the calibration design. It neither establishes a globally optimal headroom nor proves that zero empirical endpoints persist on other traffic distributions.'])
old=(ROOT/'paper_template.tex').read_text()
def section(start,end): return old[old.index(start):old.index(end)]
related=section(r'\section{Related Work and Positioning}',r'\section{System Model and Problem Definition}')
related=related.replace('ablations and fallback','ablations and risk screening')
model=section(r'\section{System Model and Problem Definition}',r'\section{Delay-Gated Action-Aware Controller}')
model=model.replace('Delay gate and','Calibrated headroom and')
model=model.replace('There\nis no cancellation, acknowledgment loss, out-of-order actuation or supersession.\nSince $L$ is fixed within each run, chronological decision order is preserved.',
    'There\nis no cancellation, acknowledgment loss or automatic supersession. Constant-delay\nruns preserve issuance order. In the variable-delay setting, $L$ is announced\nfor each issued command, activations may reorder, and commands due in the\nsame slot execute in issuance order. Future delay draws remain unavailable.')
model=model.replace(r'+\kappa\sum_{t=1}^{T-1}\norm{e(t)-e(t-1)},\qquad\kappa=0.25.',
    r'+\kappa\sum_{a\in\mathcal A_T}\norm{x_a-e_a^-},\qquad\kappa=0.25.')
model=model.replace('It includes warm-up and tail capacity, charges actual expansion changes, and',
    'The set $\\mathcal A_T$ contains all command activations within the run, $x_a$\nis the activated expansion, and $e_a^-$ is expansion immediately before that\nactivation. Every activation is charged, even when several occur in one slot.\nThe objective includes warm-up and tail capacity, charges actual changes, and')
model=model.replace('Calibration uses a 1\\% mean-miss criterion for each\nclass, but this finite-sample selection rule is not a chance constraint.',
    'Calibration uses a common 0.1\\% seed-mean miss screening target for each\nclass. This finite-sample selection rule is not a chance constraint.')
model=model.replace('$J,V_s$ &',r'$\eta,\epsilon,\delta$ & Headroom factor, absolute mean-risk target and paired miss margin\\'+'\n'+r'$J,V_s$ &')
controller=section(r'\section{Delay-Gated Action-Aware Controller}',r'\subsection{Deployment gate and comparators}')
controller=controller.replace('Delay-Gated Action-Aware Controller','Calibrated Action-Aware Controller')
controller=controller.replace(r'\frac1{D_s}\sum_i',r'\frac1{\eta D_s}\sum_i')
controller=controller.replace('candidate integer reservations yield','candidate integer reservations and headroom $\\eta$ yield')
formal=section(r'\section{Formal Properties and Limits}',r'\begin{proposition}[Pathwise fallback equivalence]')
capacity=section(r'\subsection{Capacity obstruction and computational cost}',r'\section{Experimental Method}')
capacity=capacity.replace('With two classes and three stages fixed, projection work scales with',
    r'''For disjoint service windows $I_j=[a_j,b_j+D_{\max}-1]$ containing
cohorts of size $N_j$, the same argument gives the zero-miss necessary cost bound
\begin{equation}
 J\ge\sum_i\sum_j\left[N_j-\sum_{t\in I_j}c_i(t)\right]^+.
\end{equation}
Disjointness prevents counting the same capacity opportunity twice. This lower
bound omits switching charges, competing traffic and precedence, so it is not
an achievable optimum. It applies to zero misses for those cohorts, not to
the relaxed empirical target in this experiment. No approximation ratio or
optimality gap is inferred from it.

With two classes and three stages fixed, projection work scales with''')
T=old[:old.index(r'\title{')]+FRONT+related+RELATED_ADDITION+model+controller+CALIBRATION_AND_BASELINES+formal+IRREVERSIBILITY+capacity+METHODS+RESULTS+DISCUSSION
values={'ABSTRACT_RESULT':f'Against calibrated fixed capacity, three of seven comparisons satisfy the complete descriptive screening rule and reduce mean incremental cost by {qrange}\\%.',
        'ABSTRACT_FAILURE':'Markov-modulated arrivals, compound batches and a fifty-slot actuation delay expose failures of the proposed policy\'s reliability screen.',
        'CALIBRATION_NARRATIVE':cal,'PRIMARY_NARRATIVE':primary,'SHIFT_NARRATIVE':shift,
        'ABLATION_NARRATIVE':ablation,'QUALIFIED_TABLE':'\n'.join(qt),'FULL_TABLE':unsplit(ft,'tab:allresults'),'PAIRED_TABLE':unsplit(pt,'tab:allpaired'),
        'CONCLUSION_RESULT':f'Three fixed-reference comparisons pass the complete descriptive screen, with mean cost reductions of {qrange}\\%. The same selected policy fails the absolute risk screen under Markov-modulated arrivals, compound batches and fifty-slot actuation.'}
for k,v in values.items(): T=T.replace('@@'+k+'@@',v)
T=revise(T,'\n'.join(sens)+'\n')
T=refine(T)
T=rebuild(T,OUT,D,S,ROOT)
T=enrich(T)
T=polish(T)
T=replace_schematics(T)
T=journal_revision(T,OUT,ROOT)
from final_editorial_audit import audit_editorial
T=audit_editorial(T)
keys=list(dict.fromkeys(k for match in re.findall(r'\\cite\{([^}]+)\}',T) for k in match.split(',')))
assert set(keys)==set(REFS) and len(keys)==43
assert '@@' not in T
assert 'out-of-order actuation or supersession' not in T
assert 'Calibration uses a 1\\%' not in T
def esc(v): return v.replace('&',r'\&')
bib=[r'\small\begin{thebibliography}{99}\setlength{\itemsep}{2pt}']
for key in keys:
    authors,title,venue,loc=REFS[key];link=loc if loc.startswith('http') else 'https://doi.org/'+loc
    label='Author/publisher source' if loc.startswith('http') else loc
    bib.append(r'\bibitem{'+key+'} '+esc(authors)+', ``'+esc(title)+',\'\' '+esc(venue)+'. '+r'\href{'+link+'}{'+label+'}.')
bib.extend([r'\end{thebibliography}',r'\end{document}'])
T+='\n'+'\n'.join(bib)
(OUT/'Manuscript.tex').write_text(T)
for _ in range(3):
    result=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','Manuscript.tex'],cwd=OUT,capture_output=True,text=True)
    if result.returncode: raise RuntimeError(result.stdout[-6000:])
log=(OUT/'Manuscript.log').read_text()
assert not re.search(r'(undefined references|Citation .* undefined|Reference .* undefined|Rerun to get)',log)
subprocess.run(['pdftotext','-layout','Manuscript.pdf','Manuscript.txt'],cwd=OUT,check=True)
pdftext=(OUT/'Manuscript.txt').read_text()
assert '[?]' not in pdftext and '??' not in pdftext
import fitz
pdfbytes=(OUT/'Manuscript.pdf').read_bytes()
assert pdfbytes.rstrip().endswith(b'%%EOF')
doc=fitz.open(stream=pdfbytes,filetype='pdf')
assert not doc.is_repaired and len(doc)>10
receipt=dict(pdf=str(FINAL/'Manuscript.pdf'),references=len(keys),calibration_runs=336,test_runs=840,
             qualified_fixed_settings=[SHORT[c] for c in qualified],qualified_savings=[savings(c) for c in qualified],
             unresolved_references=False,pages=len(doc),sha256=hashlib.sha256(pdfbytes).hexdigest())
(OUT/'build_receipt.json').write_text(json.dumps(receipt,indent=2))
for p in OUT.iterdir():
    if p.is_file(): os.replace(p,FINAL/p.name)
assert hashlib.sha256((FINAL/'Manuscript.pdf').read_bytes()).hexdigest()==receipt['sha256']
print(json.dumps(receipt))
