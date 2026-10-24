"""Final coherence and visual pass, preserving executed science and algorithms."""
import re
import io
import os
from pathlib import Path
from yasq_quality import algorithms

def install_plot_style():
    from matplotlib.figure import Figure
    original=Figure.savefig
    def save(fig, filename, *args, **kwargs):
        name=Path(filename).stem
        for ax in fig.axes:
            ax.set_axisbelow(True)
            ax.tick_params(labelsize=10, colors='#273444', length=3)
            ax.xaxis.label.set_size(11)
            ax.yaxis.label.set_size(11)
            for sp in ax.spines.values():
                sp.set_color('#99a4ae');sp.set_linewidth(.7)
            for line in ax.get_xgridlines()+ax.get_ygridlines():
                line.set_color('#d6dde3');line.set_alpha(.65);line.set_linewidth(.55)
            for txt in ax.texts: txt.set_fontsize(max(9,txt.get_fontsize()))
            legend=ax.get_legend()
            if legend:
                for txt in legend.get_texts():txt.set_fontsize(9)
        if name in ('reliability_primary','reliability_ablation'):
            for ax,title in zip(fig.axes,['(a) Resource cost','(b) Class 0 deadline misses','(c) Class 1 deadline misses']):
                ax.set_title(title,loc='left',fontsize=11,fontweight='bold',pad=9)
            fig.axes[0].get_legend().set_bbox_to_anchor((.5,1.35))
            fig.set_size_inches(8.7,7.4)
            fig.tight_layout(h_pad=1.7)
        if name=='headroom_sensitivity':
            for ax in fig.axes:ax.set_xlabel(r'Headroom $\eta$')
            for ax,title in zip(fig.axes,['(a) Provisioning cost','(b) Classwise risk screen']):
                ax.set_title(title,loc='left',fontsize=11,fontweight='bold',pad=10)
            fig.set_size_inches(8.5,3.8);fig.tight_layout(w_pad=2.2)
        if name=='qualified_cost':
            fig.set_size_inches(8.3,4.1)
            ax=fig.axes[0];ax.set_ylabel('Held-out setting')
            ax.set_title('Paired cost difference with 95% intervals',loc='left',fontsize=11,fontweight='bold')
            fig.tight_layout()
        if name=='calibration':
            fig.set_size_inches(8.4,4.5)
            ax=fig.axes[0]
            ax.get_legend().set_bbox_to_anchor((1,1.2))
            ax.set_ylabel('Worst class/stratum upper endpoint (%)')
            fig.tight_layout()
        if name=='screen_matrix':
            ax=fig.axes[0];ax.set_ylabel('Held-out setting')
            ax.axvline(4.5,color='#99a4ae',lw=1)
            fig.set_size_inches(9.3,4.1);fig.tight_layout()
        kwargs.update(bbox_inches='tight',pad_inches=.12)
        buffer=io.BytesIO()
        original(fig,buffer,*args,format='pdf',**kwargs)
        payload=buffer.getvalue()
        assert payload.rstrip().endswith(b'%%EOF')
        target=Path(filename)
        staging=target.with_suffix('.pdf.tmp')
        staging.write_bytes(payload)
        os.replace(staging,target)
    Figure.savefig=save

def polish(tex):
    before=algorithms(tex)
    removed=[
      'What is being orchestrated?',
      'Prediction, scheduling and interacting control actions',
      'Evidence and guarantees determine the comparison',
      'Reservations and local borrowing',
      'Command-indexed actuation and switching geometry',
      'Information-constrained design and implemented approximation',
      'Augmented state and the causal policy restriction',
      'From queue workload to the feasibility surrogate',
      'Integer service increments and score perturbations',
      'Fixed, target-utilization and queue-weighted comparators',
      'Capacity obstruction and computational cost',
      'Frozen selection, equal information and computational budget',
      'Verification and reproducibility',
      'Which fixed-reference comparisons qualify?',
      'Surrogate feasibility is not deadline reliability']
    for title in removed:
        assert r'\subsection{'+title+'}' in tex,title
        tex=tex.replace(r'\subsection{'+title+'}', '')
    titles={
      'State, service and event order':'Service chain and scheduling',
      'Age-resolved state and exact deadline accounting':'Packet ages and deadline accounting',
      'Telemetry and immutable commands':'Telemetry, actuation and switching cost',
      'Objective and measured reliability':'Objective and information-constrained formulation',
      'Finite-grid surrogate':'Finite-grid allocation and sensitivity',
      'Headroom calibration and reliability screening':'Calibration, execution and comparison policies',
      'Residual-deadline cuts and unavoidable misses':'Deadline limits and computational cost',
      'Workload, timing and held-out matrix':'Workloads and experimental controls',
      'Statistical interpretation and qualification rule':'Statistical evaluation and verification',
      'Calibration selects a policy, not a guarantee':'Calibration and qualified comparisons',
      'Traffic and delay shifts expose different failure modes':'Robustness to traffic and actuation shifts',
      'Ledger ablation: capacity reduction versus switching':'Ablations and the limits of the surrogate'}
    for old,new in titles.items():tex=tex.replace(r'\subsection{'+old+'}',r'\subsection{'+new+'}')
    bridges={
      r'\section{System Model and Problem Definition}':r'''The comparison boundary above motivates a model that separates physical packet
evolution from the information available when a command is issued. The following
formulation first specifies service and packet ages, then delayed observations
and actions, and finally the cost and reliability objective.''',
      r'\section{Calibrated Action-Aware Controller}':r'''The controller approximates the information-constrained problem using three
steps: reconstruct known action effects, rank a finite set of resource choices,
and select headroom on separate calibration runs. The projection uses only
available information, while the age-resolved model remains the reference for
measuring actual deadline outcomes.''',
      r'\section{Formal Properties and Limits}':r'''The preceding construction supports exact statements about information use,
packet conservation and the finite-grid decision. These properties are followed
by deadline-capacity bounds that identify what even a better ranking rule cannot
repair once the remaining service opportunities are insufficient.''',
      r'\section{Experimental Method}':r'''The experiments test the distinction established by the analysis: a causal,
surrogate-optimal decision need not meet packet deadlines. Nominal runs measure
cost under the common reliability screen, shifted workloads probe the deadline
limits, and ablations isolate the roles of headroom and action memory.''',
      r'\section{Results and Mechanistic Interpretation}':r'''The results follow the evaluation protocol in three stages. Calibration and
held-out screening first identify admissible cost comparisons. Traffic and delay
shifts then expose failures. Finally, ablations connect those outcomes to the
capacity, switching and workload terms in the model.'''}
    for heading,para in bridges.items():tex=tex.replace(heading,heading+'\n'+para+'\n')
    tex=tex.replace("Holm's\nprocedure \\cite{holm}",r'The sequential multiplicity-adjustment procedure in \cite{holm}')
    tex=tex.replace('The mathematical analysis connects integer reservations,\nworkload perturbations and headroom to the actual ranking rule.',
      'The mathematical analysis connects exact age-resolved service, delayed\ncommand activation and deadline-capacity limits to the implemented approximation.\nInteger reservation and sensitivity relations explain its ranking rule.')
    tex=tex.replace('The packet and command descriptions can be combined into a state',
      'To make this information restriction explicit, the packet and command\ndescriptions can be combined into a state')
    tex=tex.replace('For a fixed report state, define the unscaled service-time proxy',
      'The ranking can be interpreted through its workload-to-service ratio.\nFor a fixed report state, define the unscaled service-time proxy')
    tex=tex.replace('The fixed family enumerates all sixteen profiles',
      'The same calibration rule is applied to the following comparison families.\nThe fixed family enumerates all sixteen profiles')
    tex=tex.replace('The release runs 51 unit-test methods,',
      'Verification links this statistical protocol back to the mathematical\nmodel. Independent age-bin reconstruction checks six complete executions and\n306 stage/deadline cuts against frozen outcomes.\nThe release runs 51 unit-test methods,')
    # Macro-only algorithm improvements preserve every instruction and scope path.
    old=r'\newcommand{\algline}[3]{\node[anchor=west,font=\small] at (#2,-.48*#1) {#3};\node[anchor=east,font=\scriptsize,text=gray] at (-.15,-.48*#1) {#1}}'
    new=r'''\newcommand{\algline}[3]{\node[anchor=west,font=\fontsize{9.5}{11.5}\selectfont,text=black,inner xsep=2pt] at (#2,-.48*#1) {#3};\node[anchor=east,font=\scriptsize\sffamily,text=black!55] at (-.17,-.48*#1) {#1}}'''
    assert old in tex;tex=tex.replace(old,new)
    # Improve the explanatory introductions without changing algorithm logic.
    tex=tex.replace('The state at $t+L$ is pre-service and therefore excludes the effect\nof the new candidate command on that slot\'s service.',
      'The state at $t+L$ is pre-service and therefore excludes the effect\nof the new candidate command on that slot\'s service. Algorithm 1 takes delivered\nreports and the action ledger as inputs and returns these activation-time\nqueue estimates.')
    tex=tex.replace('optimized alternative policy family.','optimized alternative policy family. Algorithm 2 separates the offline\nselection of parameters from online command execution. The selected parameters\nremain locked throughout the held-out evaluation.')
    # A restrained shared palette, heavier paths and more space around node text.
    figs=list(re.finditer(r'\\begin\{figure\}.*?\\end\{figure\}',tex,re.S))
    for match in reversed(figs):
        f=match.group()
        if not any(r'\label{fig:'+x+'}' in f for x in ['architecture','timeline']):continue
        f=f.replace('font=\\small','font=\\small\\sffamily')
        f=f.replace('blue!45!black,line width=.7pt,rounded corners=2pt',
                    'black!65,line width=.8pt,rounded corners=1pt,fill=white,inner sep=5pt')
        f=f.replace('blue!65!black','teal!65!black').replace('orange!65!black','orange!80!black')
        f=f.replace('info/.style={->,','info/.style={->,line width=.8pt,').replace('act/.style={->,','act/.style={->,line width=.8pt,')
        f=f.replace('Dashed blue: telemetry','Dashed teal: telemetry')
        tex=tex[:match.start()]+f+tex[match.end():]
    assert algorithms(tex)==before
    # Keep the short availability note with reproduction rather than on its own page.
    availability=re.search(r'\\section\*\{Data and Code Availability\}.*?(?=\\clearpage)',tex,re.S)
    assert availability
    note=availability.group()
    tex=tex[:availability.start()]+tex[availability.end():]
    tex+='\n'+note
    assert tex.count(r'\subsection{')==13,tex.count(r'\subsection{')
    assert "Holm's" not in tex
    return tex
