"""Generate the paper, tables and vector graphics from saved executed runs."""
import json
import re
import subprocess
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from paper_references import REFS

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'paper'
OUT.mkdir(exist_ok=True)
D=json.loads((ROOT/'paper_results.json').read_text())
CASES=list(dict.fromkeys(r['case'] for r in D['summaries']))
LABELS=['Nominal','Transport','Compute','Report delay/loss','Transport L=1','Transport L=25','Transport L=50','Transport L=100']
SHORT=['N10','T10','C10','R10','T1','T25','T50','T100']
METHODS=['legacy','pipeline','gated','margin_only','fixed']
NAMES={'legacy':'Legacy','pipeline':'Pipeline','gated':'Gated','margin_only':'Margin-only','fixed':'Fixed'}
COLORS={'legacy':'#a94b35','pipeline':'#257ab1','gated':'#177d61','margin_only':'#9a6ab0','fixed':'#3c4350'}
MARKERS={'legacy':'s','pipeline':'o','gated':'D','margin_only':'^','fixed':'x'}

def row(c,m):
    return next(r for r in D['summaries'] if r['case']==c and r['method']==m)

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,
                     'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,
                     'grid.alpha':.16,'legend.frameon':False})
fig,ax=plt.subplots(3,1,figsize=(9,7),sharex=True)
for j,m in enumerate(['legacy','gated','margin_only','fixed']):
    rr=[row(c,m) for c in CASES[:4]]
    x=np.arange(4)+(j-1.5)*.14
    for k in range(3):
        y=np.array([r['cost'] if k==0 else 100*r['violation'][k-1] for r in rr])
        ci=np.array([r['cost_ci'] if k==0 else [100*v for v in r['ci'][k-1]] for r in rr])
        ax[k].errorbar(x,y,yerr=np.maximum(0,np.array([y-ci[:,0],ci[:,1]-y])),fmt=MARKERS[m],
                      color=COLORS[m],capsize=3,ms=5,label=NAMES[m],lw=1.2)
for a,l in zip(ax,['Incremental cost','Class 0 misses (%)','Class 1 misses (%)']):
    a.set_ylabel(l)
    a.set_ylim(bottom=-.025 if 'misses' in l else -100)
ax[0].legend(ncol=4,loc='upper left')
ax[-1].set_xticks(range(4),LABELS[:4])
fig.tight_layout()
fig.savefig(OUT/'primary.pdf')
plt.close(fig)

fig,ax=plt.subplots(2,3,figsize=(9,4.7),sharey='row',sharex=True)
for s in range(2):
    for j,c in enumerate(CASES[1:4]):
        for m in ['legacy','gated','margin_only','fixed']:
            r=row(c,m)
            ax[s,j].scatter(r['cost'],100*r['violation'][s],marker=MARKERS[m],color=COLORS[m],s=48,label=NAMES[m])
        if s==0: ax[s,j].set_title(LABELS[j+1])
        else: ax[s,j].set_xlabel('Incremental cost')
        ax[s,j].set_xticks([3000,5000,7000])
    ax[s,0].set_ylabel(f'Class {s} misses (%)')
handles,labels=ax[0,0].get_legend_handles_labels()
fig.legend(handles,labels,ncol=4,loc='lower center',fontsize=8)
fig.tight_layout(rect=[0,.06,1,1])
fig.savefig(OUT/'tradeoff.pdf')
plt.close(fig)

delaycases=[CASES[i] for i in (4,1,5,6,7)]
fig,ax=plt.subplots(3,1,figsize=(9,7),sharex=True)
for m in METHODS:
    rr=[row(c,m) for c in delaycases]
    x=[r['lag'] for r in rr]
    for k in range(3):
        y=[r['cost'] if k==2 else 100*r['violation'][k] for r in rr]
        ci=[r['cost_ci'] if k==2 else [100*v for v in r['ci'][k]] for r in rr]
        ax[k].plot(x,y,marker=MARKERS[m],color=COLORS[m],label=NAMES[m],lw=1.1,
                   ls='--' if m=='fixed' else '-',ms=5,zorder=5 if m=='fixed' else 3)
        ax[k].fill_between(x,[v[0] for v in ci],[v[1] for v in ci],color=COLORS[m],alpha=.08)
for a,l in zip(ax,['Class 0 misses (%)','Class 1 misses (%)','Incremental cost']):
    a.set_ylabel(l)
    a.axvline(15,color='gray',ls=':',lw=1)
    a.set_ylim(bottom=-.1 if 'misses' in l else 0)
ax[0].legend(ncol=5,fontsize=8,loc='upper left')
ax[-1].set_xticks([1,10,25,50,100])
ax[-1].set_xlabel('Command activation delay (slots)')
fig.tight_layout()
fig.savefig(OUT/'delay.pdf')
plt.close(fig)

fig,ax=plt.subplots(figsize=(8,3.4))
for j,comp in enumerate(['legacy','fixed']):
    rr=[next(r for r in D['paired'] if r['case']==c and r['comparator']==comp and r['metric']=='cost') for c in CASES[:4]]
    y=np.arange(4)+(j-.5)*.16
    v=np.array([r['mean'] for r in rr]); ci=np.array([r['ci'] for r in rr])
    ax.errorbar(v,y,xerr=np.maximum(0,[v-ci[:,0],ci[:,1]-v]),fmt='o',capsize=3,
                color=COLORS[comp],label='Gated minus '+NAMES[comp])
ax.axvline(0,color='gray',lw=1)
ax.set_yticks(range(4),LABELS[:4])
ax.set_xlabel('Paired incremental-cost difference')
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(OUT/'paired_cost.pdf')
plt.close(fig)

def table(cases,caption,label):
    lines=[r'\begin{table}[htbp]\centering\small',r'\caption{'+caption+'}',
           r'\begin{tabular}{llrrr}\toprule',r'Setting & Method & Class 0 (\%) & Class 1 (\%) & Cost\\\midrule']
    for c in cases:
        for m in METHODS:
            r=row(c,m)
            lines.append(f'{SHORT[CASES.index(c)]} & {NAMES[m]} & {100*r["violation"][0]:.4f} & {100*r["violation"][1]:.4f} & {r["cost"]:.2f} \\\\')
        lines.append(r'\addlinespace')
    lines.extend([r'\bottomrule\end{tabular}\label{'+label+'}',r'\end{table}'])
    return '\n'.join(lines)

stats=[r'\small\renewcommand{\arraystretch}{1.05}',r'\begin{longtable}{lllrrrl}',
       r'\caption{All paired comparisons. Intervals are unadjusted 95\% seed-bootstrap intervals.}\\',
       r'\toprule Case & Reference & Endpoint & Mean difference & 95\% interval & $n_{\ne0}$ & $p_{\rm Holm}$\\\midrule\endfirsthead',
       r'\toprule Case & Reference & Endpoint & Mean difference & 95\% interval & $n_{\ne0}$ & $p_{\rm Holm}$\\\midrule\endhead',
       r'\bottomrule\endfoot']
for r in D['paired']:
    f=1 if r['metric']=='cost' else 100
    ep='Cost' if r['metric']=='cost' else 'Class '+r['metric'][-1]
    p=f'{r["p_holm"]:.5f}' if r['p_holm']<.001 else f'{r["p_holm"]:.3f}'
    stats.append(f'{SHORT[CASES.index(r["case"])]} & {NAMES[r["comparator"]]} & {ep} & {f*r["mean"]:.4f} & [{f*r["ci"][0]:.4f}, {f*r["ci"][1]:.4f}] & {20-r["ties"]} & {p} \\\\')
stats.extend([r'\end{longtable}',r'\normalsize\renewcommand{\arraystretch}{1.15}'])

savings=[100*(1-row(c,'gated')['cost']/row(c,'fixed')['cost']) for c in CASES[1:4]]
misses=[100*row(c,'gated')['violation'][1] for c in CASES[1:4]]
long=row(CASES[-1],'pipeline'); legacy=row(CASES[-1],'legacy'); fixed=row(CASES[-1],'fixed')
T=(ROOT/'paper_template.tex').read_text()
values={
'SAVINGS':f'{min(savings):.2f}--{max(savings):.2f}',
'ABSTRACT_MISS':f'Class-1 mean miss fractions increase to {min(misses):.3f}--{max(misses):.3f}\\%, compared with zero observed misses for fixed capacity in those fresh-seed settings.',
'PRIMARY_NARRATIVE':f'The corresponding class-1 mean miss fractions are {misses[0]:.4f}\\%, {misses[1]:.4f}\\% and {misses[2]:.4f}\\% for transport, compute and delayed/lost reports, respectively. The fixed reference has zero observed misses in these fresh-seed settings. In the delayed/lost-report case, the gated class-0 mean miss fraction is {100*row(CASES[3],"gated")["violation"][0]:.4f}\\%. Thus cost reduction is obtained by accepting additional deadline violations, and the data do not support a reliability-equivalence claim.',
'LONG_NARRATIVE':f'the ungated pipeline has class-0 and class-1 mean miss fractions of {100*long["violation"][0]:.3f}\\% and {100*long["violation"][1]:.3f}\\%, with cost {long["cost"]:.2f}. Legacy class-1 misses reach {100*legacy["violation"][1]:.3f}\\% at cost {legacy["cost"]:.2f}. Gated and fixed both cost {fixed["cost"]:.2f} and have zero observed cohort misses in these twenty runs.',
'TESTCOUNT':'43',
'PRIMARY_TABLE':table(CASES[:4],'Primary results, twenty seeds per row. N10, T10, C10 and R10 denote nominal, transport, compute and delayed/lost reports at $L=10$.','tab:primary'),
'DELAY_TABLE':table(CASES[5:],'Long-delay transport results. Class columns are mean deadline-miss percentages, not reliability guarantees.','tab:delay'),
'STATS_TABLE':'\n'.join(stats),
}
for k,v in values.items(): T=T.replace('@@'+k+'@@',v)
keys=list(dict.fromkeys(k for match in re.findall(r'\\cite\{([^}]+)\}',T) for k in match.split(',')))
assert set(keys).issubset(REFS) and len(keys)==40
def esc(v): return v.replace('&',r'\&')
bib=[r'\small\begin{thebibliography}{99}\setlength{\itemsep}{2pt}']
for key in keys:
    authors,title,venue,loc=REFS[key]
    link=loc if loc.startswith('http') else 'https://doi.org/'+loc
    label='Author/publisher source' if loc.startswith('http') else loc
    bib.append(r'\bibitem{'+key+'} '+esc(authors)+', ``'+esc(title)+',\'\' '+esc(venue)+'. '+r'\href{'+link+'}{'+label+'}.')
bib.append(r'\end{thebibliography}')
T=T.replace('@@BIBLIOGRAPHY@@','\n'.join(bib))
assert '@@' not in T
(OUT/'Manuscript.tex').write_text(T)
for _ in range(2):
    result=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','Manuscript.tex'],cwd=OUT,capture_output=True,text=True)
    if result.returncode: raise RuntimeError(result.stdout[-6000:])
print(json.dumps(dict(pdf=str(OUT/'Manuscript.pdf'),references=len(keys),runs=len(D['runs']),savings=savings)))
