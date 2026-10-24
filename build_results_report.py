"""Create a frozen, evidence-backed results report, not a fictitious paper."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image

ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'frozen_results.json').read_text())
OUT=ROOT/'results_report'
OUT.mkdir(exist_ok=True)
CASES=list(dict.fromkeys(x['case'] for x in D['summaries']))
LABELS=['Nominal','Transport stress','Compute stress','Delayed/lost reports']
ROLES=['dynamic','selected_static','budget_static']
NAMES=['Dynamic expansion','Selected fixed expansion','Budget-matched fixed']
COLORS=['#1769aa','#c43c39','#28834a']
def row(case,role):
    return next(x for x in D['summaries'] if x['case']==case and x['role']==role)

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                     'axes.spines.right':False,'pdf.fonttype':42})
fig,axes=plt.subplots(2,1,figsize=(8,6),sharex=True)
x=np.arange(4)
for s,ax in enumerate(axes):
    for k,role in enumerate(ROLES):
        vals=[100*row(c,role)['violation'][s] for c in CASES]
        ax.bar(x+(k-1)*.23,vals,.22,label=NAMES[k],color=COLORS[k])
    ax.set_ylabel(f'Class {s} deadline misses (%)')
    ax.set_ylim(bottom=0)
axes[0].legend(frameon=False,loc='upper left',fontsize=8)
axes[-1].set_xticks(x,LABELS)
fig.tight_layout()
fig.savefig(OUT/'classwise_results.pdf')
fig.savefig(OUT/'classwise_results.png',dpi=240)
plt.close(fig)
fig,ax=plt.subplots(figsize=(8,3))
for k,role in enumerate(ROLES):
    ax.bar(x+(k-1)*.23,[row(c,role)['cost'] for c in CASES],.22,label=NAMES[k],color=COLORS[k])
ax.set_ylabel('Incremental cost (abstract units)')
ax.set_xticks(x,LABELS)
ax.legend(frameon=False,fontsize=8)
fig.tight_layout()
fig.savefig(OUT/'incremental_cost.pdf')
fig.savefig(OUT/'incremental_cost.png',dpi=240)
plt.close(fig)

pdfmetrics.registerFont(TTFont('Body',font_manager.findfont('DejaVu Sans')))
pdfmetrics.registerFont(TTFont('BodyBold',font_manager.findfont(font_manager.FontProperties(family='DejaVu Sans',weight='bold'))))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='Body',boldItalic='BodyBold')
styles=getSampleStyleSheet()
for style in styles.byName.values():
    if hasattr(style,'fontName'):
        style.fontName='BodyBold' if 'Bold' in style.fontName else 'Body'
styles.add(ParagraphStyle(name='TitleCustom',fontName='BodyBold',fontSize=22,leading=26,
                         textColor=colors.HexColor('#17364a'),spaceAfter=14))
styles.add(ParagraphStyle(name='Deck',fontName='Body',fontSize=11,leading=15,spaceAfter=12))
styles.add(ParagraphStyle(name='CellCustom',fontName='Body',fontSize=8,leading=10))
styles['BodyText'].fontSize=10
styles['BodyText'].leading=14
styles['BodyText'].spaceAfter=9
styles['Heading2'].textColor=colors.HexColor('#17364a')
def p(text,style='BodyText'):
    return Paragraph(text,styles[style])
def table(data,widths):
    t=Table([[p(str(x),'CellCustom') for x in r] for r in data],colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('LINEABOVE',(0,0),(-1,0),1,colors.black),
                           ('LINEBELOW',(0,0),(-1,0),.7,colors.black),
                           ('LINEBELOW',(0,-1),(-1,-1),.7,colors.black),
                           ('VALIGN',(0,0),(-1,-1),'TOP'),
                           ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    return t
story=[]
story += [p('Frozen Simulation Results','TitleCustom'),
          p('Two-class resource allocation and bounded capacity elasticity','Deck'),
          p('Student: Fatima Subhi Khaleel<br/>Research direction: SDN-managed O-RAN orchestration<br/>Evaluation freeze: 18 October 2026','Deck'),
          p('1. Scope and decision','Heading2'),
          p('<b>The experiment is complete for the implemented abstraction. The results are not validated O-RAN network results and are not yet sufficient for a submission-ready Transactions paper.</b>'),
          p('This report freezes the code, comparator selection, raw outputs and interpretation. It does not rename a synthetic queueing experiment as a physical-layer or O-RAN protocol simulation.'),
          p('2. Independent evaluation design','Heading2'),
          table([['Element','Frozen choice'],['Calibration','Five seeds: 4000-4004; all 16 fixed transport/compute additions plus dynamic expansion'],
                 ['Evaluation','Twenty different seeds: 5000-5019; four settings and four comparison roles'],
                 ['Total new runs',f"{len(D['calibration_runs'])} calibration + {len(D['heldout_runs'])} held-out"],
                 ['Measured cohort','300-slot warmup; 3000-slot arrivals; 40-slot followup; 20-ms synthetic slots'],
                 ['Static selection','Cheapest fixed addition with both calibration class means at or below 1%; fallback minimizes worst class mean'],
                 ['Budget comparator','Best calibration-weighted fixed allocation whose incremental cost is no greater than the calibration dynamic mean cost'],
                 ['Controller','19 class shares; bounded additions of 0-3 units per transport/compute stage; ten-slot actuation delay']], [105,390]),
          Spacer(1,10),p('The 1% value is a comparator-selection criterion on sample means. It is not a proven SLA, and comparator selection never uses held-out outcomes.')]
story += [PageBreak(),p('3. Held-out numerical results','TitleCustom')]
data=[['Setting / method','Fixed addition','Class 0 (%)','Class 1 (%)','Extra cost']]
for i,c in enumerate(CASES):
    for role,n in zip(ROLES,NAMES):
        r=row(c,role)
        data.append([LABELS[i]+' / '+n,r['config'],f"{100*r['violation'][0]:.3f}",f"{100*r['violation'][1]:.3f}",f"{r['cost']:.2f}"])
story += [table(data,[180,100,65,65,85]),Spacer(1,10),
          p('Cost includes incremental provisioned capacity and changes only, across warmup, measurement and followup. It excludes base infrastructure costs and uses abstract units, not currency.'),
          p('4. Independent paired comparison','Heading2')]
data=[['Setting','Dynamic - selected fixed, class 0 (pp)','Class 1 (pp)','Incremental cost saving']]
for i,c in enumerate(CASES):
    new,old=row(c,'dynamic'),row(c,'selected_static')
    def ci(metric):
        z=next(x for x in D['paired_comparisons'] if x['case']==c and x['comparator']=='selected_static' and x['metric']==metric)
        return f"{100*z['difference']:+.3f} [{100*z['ci95'][0]:+.3f}, {100*z['ci95'][1]:+.3f}]"
    saving=f"{100*(1-new['cost']/old['cost']):.2f}%" if old['cost'] else 'Not defined: fixed cost is zero'
    data.append([LABELS[i],ci('class0'),ci('class1'),saving])
story += [table(data,[105,135,135,120]),Spacer(1,10),
          p('Brackets contain exploratory 95% paired seed-bootstrap intervals (2000 resamples). No multiplicity correction or non-inferiority test is applied. A zero bootstrap interval after zero observations does not establish zero true failure probability. Budget matching uses calibration mean cost, not a hard held-out cost equality.')]
story += [PageBreak(),p('5. Classwise performance','TitleCustom'),
          Image(str(OUT/'classwise_results.png'),width=495,height=371),
          p('Figure 1. Both service classes are retained. Values are held-out seed means, with identical exogenous events and report request/loss budgets across comparison roles.'),
          p('Do not infer that a zero-height bar is a formal reliability guarantee. The finite simulation can fail to observe rare events, and its synthetic workload does not cover real network distributions.')]
story += [PageBreak(),p('6. Resource cost','TitleCustom'),
          Image(str(OUT/'incremental_cost.png'),width=495,height=186),
          p('Figure 2. Incremental resource cost for the independently selected fixed comparator, budget-matched fixed comparator and dynamic policy. A lower cost must be considered alongside both classwise violation rates.'),
          p('7. Interpretation of the earlier saving claim','Heading2'),
          p('The earlier 80-81% saving was measured against permanently maximum additions of three units at each expandable stage. It was not a saving against the cheapest adequate fixed allocation. This report replaces that weak comparison with a calibration-selected fixed baseline and independent evaluation. Any paper must use the stronger comparison and report adverse outcomes.'),
          p('Nominal overhead','Heading2'),
          p('Fixed zero expansion can already meet all observed nominal deadlines. Any nonzero nominal dynamic expansion is additional cost without an observed quality benefit. It must be retained in the evaluation, not excluded as an inconvenient case.')]
story += [PageBreak(),p('8. Publication-readiness audit','TitleCustom'),
          table([['Requirement','Current evidence / gap'],
                 ['Reproducible execution','Source, full per-seed output, independent selection, paired intervals, trace hashes and version-preserved baselines are supplied.'],
                 ['Internal verification','24 unit tests from the previous stages plus six static-engine numeric regression comparisons. Runtime conservation and capacity assertions execute in all runs.'],
                 ['Radio realism','No SINR, fading, interference, modulation/coding, retransmission or resource-block model. Radio is an abstract service queue.'],
                 ['Compute and transport','Packets require one service unit at each stage. No calibrated bit sizes, CPU cycles, propagation or telemetry bandwidth cost.'],
                 ['O-RAN integration','No E2/O1/O2 implementation, actual RIC deployment, SDN flow rules or cloud provisioner. Control split is conceptual.'],
                 ['Theoretical guarantees','Delay estimates and uncertainty margins are uncalibrated surrogates. Grid optimality is not optimality of the real network or a chance-constraint proof.'],
                 ['Literature and novelty','No systematic full-text closest-work comparison or same-journal evidence review is completed in this package.'],
                 ['External validation','No trace-calibrated workload, protocol emulator or real testbed cross-check.']], [110,385]),
          Spacer(1,12),p('<b>Decision:</b> retain these outputs as frozen results of the abstract model. Do not label them final publishable O-RAN results. Publication readiness requires a validated model and external comparisons, not merely more seeds or cosmetic figures.'),
          p('9. Integrity and reproduction','Heading2'),
          p('Run frozen_evaluation.py to reproduce comparator selection and evaluation; run build_results_report.py to rebuild this report. Parameters and selection criteria are in the source. An integrity manifest records the input/output SHA-256 hashes. Raw files remain authoritative over rounded table values.')]

def footer(canvas,doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#c0c8ce'))
    canvas.line(50,43,545,43)
    canvas.setFont('Body',8)
    canvas.drawString(50,30,'Fatima Subhi Khaleel | Frozen abstract-model evaluation')
    canvas.drawRightString(545,30,str(doc.page))
    canvas.restoreState()

SimpleDocTemplate(str(OUT/'Simulation_Results_Report.pdf'),pagesize=(595,842),
                  rightMargin=50,leftMargin=50,topMargin=45,bottomMargin=60).build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT/'Simulation_Results_Report.pdf')
