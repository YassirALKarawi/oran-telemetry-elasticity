"""Rebuild the argument and results around frozen evidence, not extra claims."""
import re
import json
import hashlib
import statistics as st
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from yasq_quality import algorithms

INTRO = r'''
\section{Introduction}
An elastic resource controller acts on two different timelines. Its queue report
describes a past state, whereas its next command changes a future service
opportunity. Between those instants, earlier commands can already have altered
capacity. Open Radio Access Network (O-RAN) exposes programmable control across
disaggregated components \cite{polese}. Software-defined networking (SDN)
separates control from forwarding \cite{sdn}, and virtualization makes resource
provisioning an explicit orchestration decision \cite{ecosystem}. These features
motivate accounting for the gap between observing, requesting and activating
resources. They do not make those three events simultaneous.

The resulting ambiguity is operationally important. A controller extrapolating
an old service rate may request capacity that is already scheduled to arrive.
Conversely, a controller that assumes immediate activation may underestimate
the workload accumulated before its command becomes effective. Information-age
analysis characterizes observation freshness \cite{age}, networked control
incorporates delayed feedback \cite{networked}, and predictive control uses
models of future action effects \cite{mpc}. The unresolved question for the
present experiment is narrower: how much does explicitly retaining the known
action history contribute to the cost--deadline trade-off of an otherwise
simple allocator?

That question requires a reliability-aware comparison. Reducing active capacity
almost automatically reduces a capacity-based cost, but can also increase
deadline misses. A lower cost alone is therefore not evidence of a better
allocator. The experiment separates three objects: the stochastic design
objective, the finite-grid proxy used to issue commands, and the empirical
screen used to interpret measured outcomes. This separation prevents a
surrogate-feasible decision or a favorable average cost from being mistaken
for a packet-level guarantee.

The study considers two packet classes traversing three serial service stages,
motivated by access, transport and compute domains. The controller receives
one delayed stage report per control epoch, projects workloads through already
applied and pending commands, and chooses expansion and class reservations.
A headroom parameter is selected on calibration seeds and locked before
testing. All stages use abstract packet-service units. Physical radio channels,
processor execution times and O-RAN interface interoperability are outside
the implemented model.

Three research questions organize the analysis. First, can the calibrated
controller reduce cost against a preprovisioned reference while both pass the
same classwise reliability screen? Second, is the ledger useful at fixed
headroom, and how much of its cost difference comes from capacity versus
switching? Third, do shifted arrival patterns, bottleneck location and command
delay reveal a gap between proxy feasibility and measured deadline risk?

The contributions are an executable action-ledger controller, an explicit
calibration-and-comparison protocol, and a reproducible account of its useful
and failing regimes. The mathematical analysis connects integer reservations,
workload perturbations and headroom to the actual ranking rule. The numerical
analysis covers 336 calibration and 840 held-out executions, with matched
traces, component ablations and seed-level uncertainty. Additional diagnostic
decompositions use these saved executions without changing parameter selection
or the original qualification rule. The contribution is this controlled
combination, not a new prediction paradigm, a solution to the full stochastic
control problem, or demonstrated superiority over deployed O-RAN systems.

The remainder develops the literature-based comparison boundary, the service
and information model, the controller and its analytical limits, and the
experimental evidence. Successful comparisons and counterexamples receive
separate treatment before the deployment limitations are discussed.
'''

RELATED = r'''
\section{Related Work and Comparison Boundary}
\subsection{What is being orchestrated?}
OrchestRAN chooses intelligence algorithms and their execution locations
\cite{orchestr}, while OREO orchestrates and shares near-real-time control
applications (xApps) across network services \cite{oreo}. Their decision objects
are not the packet-stage capacities used here. Joint cloud, fronthaul and radio
orchestration already treats cross-domain resource coupling \cite{demir}.
Consequently, neither a three-domain drawing nor joint resource selection is
the novelty of the present study. The relevant distinction is explicit replay
of already issued commands when stale queue measurements are projected.

Implemented virtualized radio access network (vRAN) systems provide a stronger
physical basis than homogeneous queues. vrAIn learns radio/computing allocation
\cite{vrain}, Nuberu restructures processing under compute deficits
\cite{nuberu}, and Concordia schedules shared computing against processing
deadlines \cite{concordia}. Online-learning base-station allocation
\cite{kalntis} and MAREA's delay-aware multi-timescale orchestration
\cite{marea} further constrain the novelty claim: adaptation and delay-aware
allocation are established approaches. Proactive workload orchestration
\cite{caora} and learned functional-split selection \cite{murti} also address
anticipation and reconfiguration. None of their reported performance numbers
can be compared directly with an abstract service-unit cost.

\subsection{Prediction, scheduling and interacting control actions}
Radio-intelligence-controller allocation \cite{wang}, multivariate
probabilistic forecasting \cite{kasuluru}, and online-learning energy-aware
allocation \cite{sora} differ in both prediction machinery and objective.
The predictor here holds reported ingress and base capacity constant. Its
added information is the controller's own action history, not a learned model
of future traffic. This permits an inspectable ablation, but leaves uncertainty
from workload evolution unresolved.

COMIX studies interactions between xApps \cite{comix}. In contrast, this paper
tracks sequential commands from a single controller. Service-enabled sub-slice
isolation \cite{5erasi} and RadioSaber's channel-aware customizable schedulers
\cite{radiosaber} also provide capabilities that quota borrowing does not
establish. EdgeRIC demonstrates control in an implemented low-latency system
\cite{edgeric}. Its evidence motivates examining delay, but does not justify
assigning a measured real-time meaning to the synthetic slot used below.

\subsection{Evidence and guarantees determine the comparison}
ColO-RAN \cite{coloran}, OpenRAN Gym \cite{gym}, SCOPE \cite{scope} and FlexRIC
\cite{flexric} offer programmable experimental foundations. ns-O-RAN
\cite{nsoran}, Colosseum \cite{colosseum} and the 5G-LENA simulator
\cite{lena}, including its calibration studies \cite{calibration}, identify
possible routes to higher-fidelity validation. These are not platforms executed
in the current study. Listing them does not establish interface compliance.

Queue-based stochastic optimization \cite{neely}, deterministic network calculus
\cite{netcalc} and stochastic network calculus \cite{stochcalc} address distinct
types of guarantees. Analyses of interleaved weighted round-robin \cite{iwrr},
deficit round-robin \cite{drr} and packet-level delay bounds \cite{packetbounds}
depend on precise arrival and service assumptions. The workload score in this
paper is not a service curve, a stability proof or a probabilistic delay bound.
Verification of its implementation is also different from physical validation
of the abstraction \cite{sargent}.

The executed comparator families are deliberately transparent. Kubernetes
Horizontal Pod Autoscaling (HPA) supplies the target-utilization and downscale
stabilization ideas \cite{hpa}. Drift-plus-penalty (DPP) scheduling supplies the
queue-weighted resource-cost trade-off \cite{dppenergy}. Both implementations
below are adaptations, with changed metrics and timing, rather than reproductions
of the original systems or their guarantees. Delay-Tolerant Constrained Online
Convex Optimization (DTC-OCO) studies delayed feedback with constraint and regret
analysis \cite{dtc}. Delayed activation of immutable integer commands is a
different decision setting, so DTC-OCO is positioning literature only.

Table~\ref{tab:related} makes the comparison boundary explicit. The empirical
gap addressed here is the joint accounting of stale reports, known pending
commands and a common reliability screen in a reproducible queue experiment.
It is not a claim that prior systems omit all of these concerns, nor a claim
of state-of-the-art performance without reproducing them.
\begin{table}[!htbp]\centering\small
\caption{Decision and evidence boundaries of the closest research directions.}
\label{tab:related}
\begin{tabular}{>{\raggedright\arraybackslash}p{30mm}>{\raggedright\arraybackslash}p{49mm}>{\raggedright\arraybackslash}p{70mm}}
\toprule Direction & Established focus & Permissible comparison in this study\\\midrule
OrchestRAN, OREO & Intelligence placement and xApp service orchestration & Conceptual positioning only. Packet capacity is a different decision object.\\
vrAIn, Nuberu, Concordia & Implemented radio/compute coupling and processing deadlines & Motivation for resource coupling. No matched physical benchmark is claimed.\\
MAREA, online allocation & Delay-aware orchestration and adaptive resource selection & Distinguishes analytical guarantees from the present workload heuristic.\\
Probabilistic forecasting, EdgeRIC & Richer predictors or implemented real-time control & Defines omitted capabilities. No accuracy or latency superiority is inferred.\\
HPA, DPP families & Utilization sizing and queue-weighted cost control & Executed as explicitly specified adaptations on common traces and grids.\\
Present study & Ledger replay, locked headroom, matched traces and classwise screens & Conditional cost evidence, paired ablations and retained failure regimes.\\
\bottomrule\end{tabular}\end{table}
'''

MATH = r'''
\subsection{Integer service increments and score perturbations}
The ranking is discrete, so a smooth derivative alone cannot describe its
response to one added capacity unit. For two classes with integer total
capacity $C$ and weights $(w_0,w_1)=(\alpha,1-\alpha)$, define proportional
quotas $r_s=Cw_s/(w_0+w_1)$, fractional parts $f_s=r_s-\lfloor r_s\rfloor$
and remainder $\nu=C-\sum_s\lfloor r_s\rfloor$. Largest-remainder allocation gives
\begin{equation}
 g_0(C,\alpha)=\lfloor r_0\rfloor+\nu\mathbf1\{f_0\ge f_1\},
 \qquad g_1(C,\alpha)=C-g_0(C,\alpha).
 \label{eq:integerquota}
\end{equation}
To obtain this expression, floor both proportional quotas and allocate any
remaining unit to the larger fractional part, using class index for equality.
This explains the plateaus and jumps as $\alpha$ changes. In exact arithmetic,
$g_0=\lfloor\alpha C+1/2\rfloor$. Reproduction uses the computed fractional
parts instead: binary floating-point values can distinguish a mathematical
tie. For example, the saved implementation returns $(3,2)$ at $C=5$ and
$\alpha=0.70$. The executed allocation routine is retained unchanged, and
\eqref{eq:integerquota} is checked against it throughout the relevant grid.

For fixed demand and a fixed share, compare candidate capacities $C_i$ and
$C_i+1$. Define the corresponding floored denominators as
$\widetilde g_{is}$ and $\widetilde g'_{is}$, as in
\eqref{eq:worktime}. Their exact contribution to the class-score change is
\begin{equation}
 \rho_s'-\rho_s
 =-\frac{d_{is}(\widetilde g'_{is}-\widetilde g_{is})}
 {\eta D_s\widetilde g_{is}\widetilde g'_{is}}.
 \label{eq:discretemarginal}
\end{equation}
This follows by subtracting the two reciprocal service terms. An added unit
can leave one class's score unchanged if its reservation does not increase.
Its effect is amplified when it removes a zero reservation, where the numerical
denominator floor is active. Thus a common share and an integer service budget
couple the two classes even though the score is computed classwise. The
quantity in \eqref{eq:discretemarginal} is a proxy improvement, not an observed
change in packet latency.

The score also permits a finite perturbation bound. At fixed candidate
reservations, let $E^q_{is}$, $E^a_{is}$ and $E^v_{is}$ bound the absolute
differences between two projected queues, mean-ingress estimates and
nonnegative net-flow variance estimates. From \eqref{eq:demand}, the triangle
inequality and $|\sqrt{v'}-\sqrt v|\le\sqrt{|v'-v|}$ give
\begin{align}
 |d'_{is}-d_{is}|&\le E^q_{is}+hE^a_{is}+\sqrt{hE^v_{is}},
 \label{eq:demanderror}\\
 |\rho_s'-\rho_s|&\le B_s
 :=\frac1{\eta D_s}\sum_i
 \frac{E^q_{is}+hE^a_{is}+\sqrt{hE^v_{is}}}{\widetilde g_{is}}.
 \label{eq:scoreerror}
\end{align}
If such bounds were available and $\rho_s+B_s\le1$ for both classes, the
same candidate would remain surrogate-feasible under those perturbations.
No such error bounds were calibrated or enforced in the executed controller.
This is an analytical diagnostic, not a newly implemented robust policy.

Equation~\eqref{eq:scoreerror} connects the sensitivity analysis to the test
design. At equal reservations and error magnitudes, the shorter deadline
$D_0=15$ amplifies score perturbations by $D_1/D_0=8/3$ relative to $D_1=40$.
Meanwhile, the projection horizon is $\Delta_i+L$, but the dispersion allowance
uses only $h=5$. Increasing $L$ therefore extends exposure to unmodeled
ingress changes without automatically enlarging that allowance. The ledger
removes ambiguity about known actions, not uncertainty about future traffic.
This distinction motivates examining both proxy-feasibility frequency and
actual misses in the results.
'''

DISC = r'''
\section{Discussion and Deployment Boundary}
The supported advantage is conditional. P and R test repeatability within
the calibration traffic constructions, while J tests one announced-delay
law. Failures in M, B and L prevent extrapolation to general workload or
latency robustness. Integer reservations, headroom and ledger replay explain
how decisions are formed. Their consistency with aggregate results does not
identify forecast accuracy or establish packet-level guarantees.

Six seeds per calibration stratum, twenty per test setting, all-zero samples
and unadjusted comparisons limit inference at the 0.1\% target. The fixed
reference has its own share policy, and HPA/DPP are adaptations. Neither
competitive-system reproduction nor physical O-RAN validation is provided.
The next validation steps are measured service and interface-delay mappings,
recorded workloads, independently implemented baselines and larger reliability
experiments. Channel variation, retransmissions and virtualization interference
must enter that model before interpreting abstract cost as deployment benefit.

\section{Conclusion}
The action-ledger controller separates measured, requested and activated
capacity. With independently calibrated headroom, it yields qualified cost
reductions of 35.61--37.73\% against fixed provisioning in three of seven
synthetic settings. Its nominal ledger ablation saves approximately 9.96\%,
primarily through lower active capacity, with zero observed misses for both
variants. Shifted traffic and long actuation nevertheless expose deadline
failures despite frequent surrogate-feasible decisions. The resulting
contribution is an auditable controller and a reproducible boundary on its
empirical benefit, not a deadline certificate or demonstrated superiority
over deployed O-RAN systems.

\section*{Data and Code Availability}
The archive provides code, the frozen protocol, all 1176 execution records,
verification tests, manuscript sources and vector figures. Additional
diagnostics reuse those records. Historical studies remain separate. No
external dataset or public archival identifier is asserted.
'''

def extract_figure(tex,label):
    return next(m.group() for m in re.finditer(r'\\begin\{figure\}.*?\\end\{figure\}',tex,re.S) if r'\label{'+label+'}' in m.group())

def extract_table(tex,label):
    return next(m.group() for m in re.finditer(r'\\begin\{table\}.*?\\end\{table\}',tex,re.S) if r'\label{'+label+'}' in m.group())

def rebuild(tex, out, data, selection, root):
    algs=algorithms(tex)
    assert len(algs)==2
    # Snapshot each preserved block in the build receipt for direct comparison.
    alg_hashes=[hashlib.sha256(a.encode()).hexdigest() for a in algs]
    tex=tex[:tex.index(r'\section{Introduction}')]+INTRO+RELATED+tex[tex.index(r'\section{System Model and Problem Definition}'):]
    tex=tex.replace(r'\subsection{Headroom calibration and reliability screening}',MATH+r'\subsection{Headroom calibration and reliability screening}')
    # Remove duplicated general objective prose now that the formal target exists.
    tex=tex.replace('The ideal design problem minimizes expected $J$ under classwise reliability\nrequirements using only available information. The implemented method does not\nsolve that stochastic control problem. It solves the per-decision surrogate\ndefined next, and its actual reliability is measured separately.','')
    cases=list(dict.fromkeys(r['case'] for r in data['summaries']))
    labels=list('PMBCRLJ')
    def row(c,m): return next(r for r in data['summaries'] if r['case']==c and r['method']==m)
    def pair(c,m): return next(r for r in data['paired'] if r['case']==c and r['comparator']==m)
    def records(c,m): return [r for r in data['runs'] if r['case']==c and r['method']==m]
    methods=['risk','no_ledger','uncalibrated']
    colors=['#14785e','#2784a7','#b64447']
    names=['Ledger, calibrated','No ledger','Ledger, uncalibrated']
    diagnostics=[]
    for c,l in zip(cases,labels):
        for m in methods:
            rr=records(c,m)
            capacity=st.fmean(r['extra_service_unit_slots'] for r in rr)
            switching=.25*st.fmean(r['activation_switching_units'] for r in rr)
            assert abs(capacity+switching-row(c,m)['cost'])<1e-8
            diagnostics.append(dict(setting=l,method=m,capacity_cost=capacity,switching_cost=switching,
                feasible_percent=100*st.fmean(r['modeled_feasible_checks']/r['modeled_feasibility_checks'] for r in rr),
                worst_class_mean_percent=100*max(row(c,m)['violation'])))
    def diag(l,m): return next(r for r in diagnostics if r['setting']==l and r['method']==m)
    plt.rcParams.update({'font.size':10,'axes.labelsize':10,'xtick.labelsize':10,'ytick.labelsize':9,'legend.fontsize':9})
    fig,axes=plt.subplots(1,2,figsize=(9.5,3.8),gridspec_kw={'width_ratios':[1.5,1]})
    for j,(m,color,name) in enumerate(zip(methods,colors,names)):
        rr=[diag(l,m) for l in labels]; x=np.arange(7)+(j-1)*.23
        cap=np.array([r['capacity_cost'] for r in rr]);sw=np.array([r['switching_cost'] for r in rr])
        axes[0].bar(x,cap,width=.21,color=color,label=name)
        axes[0].bar(x,sw,bottom=cap,width=.21,color='white',edgecolor=color,hatch='////',linewidth=.8)
        axes[1].plot(labels,[r['switching_cost'] for r in rr],'-o',color=color,ms=4,label=name)
    axes[0].set_xticks(range(7),labels);axes[0].set_ylabel('Mean incremental cost');axes[0].set_ylim(0,6800)
    axes[0].set_title('(a) Active capacity + switching',loc='left',fontsize=10,fontweight='bold')
    axes[1].set_title('(b) Switching component',loc='left',fontsize=10,fontweight='bold');axes[1].set_ylabel('Mean switching cost')
    for ax in axes: ax.set_xlabel('Held-out setting');ax.set_axisbelow(True)
    fig.legend(*axes[0].get_legend_handles_labels(),loc='upper center',ncol=3,bbox_to_anchor=(.5,1.04))
    fig.tight_layout(rect=(0,0,1,.95));fig.savefig(out/'cost_components.pdf');plt.close(fig)
    # Gate matrix: an exact rendering of the existing, unchanged rule.
    gates=[]
    for c in cases:
        p=pair(c,'fixed')
        g=[data['selected']['risk'] is not None and data['selected']['fixed'] is not None,
           max(row(c,'risk')['upper95'])<=.001,max(row(c,'fixed')['upper95'])<=.001,
           max(p['miss_upper95'])<=.001,p['cost_ci'][1]<0]
        gates.append(g+[all(g)])
    fig,ax=plt.subplots(figsize=(9.3,3.4))
    for i in range(7):
        for j in range(6):
            yes=gates[i][j]
            ax.scatter(j,i,s=140,marker='o' if yes else 'X',color='#14785e' if yes else '#b64447')
    ax.set_xticks(range(6),['Calibration\nboth pass','Proposed\nabsolute risk','Fixed\nabsolute risk','Paired\nmiss margin','Paired\ncost < 0','Complete\nscreen'])
    ax.set_yticks(range(7),labels);ax.invert_yaxis();ax.set_xlim(-.5,5.5)
    ax.grid(axis='x',alpha=.2);ax.set_title('Filled circle: pass     Cross: fail',loc='left',fontsize=10)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(length=0);fig.tight_layout();fig.savefig(out/'screen_matrix.pdf');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.8,3.6))
    for m,color,name,marker in zip(methods,colors,names,['o','s','^']):
        rr=[diag(l,m) for l in labels]
        ax.scatter([r['feasible_percent'] for r in rr],[r['worst_class_mean_percent'] for r in rr],color=color,marker=marker,s=52,label=name)
        if m=='risk':
            for r in rr:
                dx,dy={'P':(-14,-14),'C':(7,5),'M':(7,5),'B':(7,-13),'R':(7,3),'J':(-15,-12),'L':(7,4)}[r['setting']]
                ax.annotate(r['setting'],(r['feasible_percent'],r['worst_class_mean_percent']),xytext=(dx,dy),textcoords='offset points',fontsize=9)
    ax.axhline(.1,ls='--',color='#555555',lw=1)
    ax.set_yscale('symlog',linthresh=.01);ax.set_yticks([0,.01,.1,1,10],[0,.01,.1,1,10]);ax.set_ylim(-.002,25)
    ax.set_xlabel('Mean fraction of control epochs declared surrogate-feasible (%)')
    ax.set_ylabel('Worse class mean miss percentage');ax.legend(ncol=3,loc='upper left',bbox_to_anchor=(0,1.15))
    ax.set_xlim(78,98);fig.tight_layout();fig.savefig(out/'proxy_vs_outcome.pdf');plt.close(fig)
    figures={l:extract_figure(tex,'fig:'+l) for l in ['calibration','headroom','primary','qualified','ablation']}
    tables={l:extract_table(tex,'tab:'+l) for l in ['headroom','qualified']}
    nominal=diag('P','risk'); noledger=diag('P','no_ledger')
    # All new scalar claims below are generated from frozen records.
    capacity_difference=noledger['capacity_cost']-nominal['capacity_cost']
    switch_difference=noledger['switching_cost']-nominal['switching_cost']
    share=100*capacity_difference/(capacity_difference+switch_difference)
    result=r'''\section{Results and Mechanistic Interpretation}
\subsection{Calibration selects a policy, not a guarantee}
The selected fixed expansion is $(x_2,x_3)=(2,0)$, the selected headroom is
$\eta=0.75$, and the selected utilization is $u=0.85$. No DPP-inspired candidate
passes both calibration strata, so price $v=0.1$ remains diagnostic only.
Figure~\ref{fig:calibration} reports all candidates, including failed choices.
The three lower headroom values pass the empirical calibration screen. The
$\eta=1$ variant does not. Selection minimizes cost among passing grid points,
not over an unknown continuous optimum or a confidence-certified feasible set.
''' + figures['calibration']+r'''
Table~\ref{tab:headroom} and Figure~\ref{fig:headroom} isolate the headroom sweep
on identical calibration seeds. Tightening $\eta$ contracts the candidate set
in \eqref{eq:feasibleset}, which is consistent with higher observed resource
cost. The values $0.25$ and $0.50$ purchase substantially more capacity than
$0.75$ without improving their already-zero empirical miss endpoints. Those
zeros do not establish equal true risk. At $\eta=1$, reduced provisioning is
accompanied by failed endpoints. The trade-off is therefore substantive, not
merely a tunable score with no connection to packet outcomes.
''' + tables['headroom']+figures['headroom']+r'''
\subsection{Which fixed-reference comparisons qualify?}
Figure~\ref{fig:screen} renders every part of the unchanged comparison rule.
The paired cost condition passes in all seven settings. Reliability, not the
sign of the cost difference, determines which savings can be qualified.
P, R and J pass every condition. M, B and L fail the proposed absolute-risk
screen, while C fails because the fixed reference exceeds its class-1 target.
This is why the zero observed misses of the proposed policy in C do not
produce a qualified comparison under the declared rule.
\begin{figure}[!htbp]\centering
\includegraphics[width=.98\linewidth]{screen_matrix.pdf}
\caption{Qualification of proposed versus fixed capacity, decomposed by condition.}
\label{fig:screen}\end{figure}
''' + tables['qualified']+r'''
Table~\ref{tab:qualified} supplies the endpoints behind that decision. In P,
mean cost is 4159.85 versus 6680.00 for fixed provisioning. The paired difference
is $-2520.15$, with a 95\% interval approximately $[-2593.1,-2447.0]$.
Qualified savings are 37.73\% in P, 37.10\% in R and 35.61\% in J.
Figure~\ref{fig:qualified} shows why negative cost differences in the other
settings must remain unqualified. These comparisons use common thresholds,
not proof that the policies have identical underlying reliability.
''' + figures['qualified']+r'''
\subsection{Traffic and delay shifts expose different failure modes}
Figure~\ref{fig:primary} separates resource cost from each class's miss fraction.
Under Markov traffic M, proposed mean misses are 0.0915\% and 0.8811\%.
Under compound batches B, they are 0.3413\% and 0.1297\%. Their upper endpoints
fail the target. Mean-matched burst states therefore do not preserve the
periodic calibration result. Both the duration of unfavorable service periods
and the arrival process seen by each queue matter.
''' + figures['primary']+r'''
For batch size $b=3$, conditional arrivals are $A_s=bK_s$ with
$K_s\sim\operatorname{Poisson}(\lambda_s/b)$. Hence
\begin{equation}
 \mathbb E[A_s\mid\lambda_s]=\lambda_s,\qquad
 \operatorname{Var}(A_s\mid\lambda_s)=b\lambda_s.
 \label{eq:batchmoments}
\end{equation}
The compound case changes dispersion without changing conditional mean.
However, the reported $v_{is}$ measures net ingress minus service, not arrival
variance alone. Reservations and borrowing also change with the resulting
queue trajectories. The opposite movements of the two class means between M
and B therefore cannot be summarized as a monotone classwise variance effect.

In L, $L=50$ exceeds both deadlines, and class-1 mean misses reach 8.7846\%
versus 0.0208\% for fixed provisioning. The irreversibility property explains
the timing obstruction: a new command cannot change service before activation.
The horizon mismatch in \eqref{eq:scoreerror} provides an additional reason
not to interpret a bounded dispersion term as protection against this delay.
J instead mixes shorter and longer delays, has mean 18.2 slots, and announces
each delay on issue. Its successful screen neither contradicts L nor isolates
the effect of jitter at equal mean delay.

\subsection{Ledger ablation: capacity reduction versus switching}
Figure~\ref{fig:ablation} compares the proposed controller with a rate-only
projection at the same headroom and with an uncalibrated ledger variant.
In P, the no-ledger cost is 4619.93 versus 4159.85 for the proposed policy,
approximately a 9.96\% reduction. Both have zero observed misses. The
uncalibrated controller is cheaper at 2737.40, but its class means become
0.0570\% and 0.1447\%. The two ablations answer different questions:
ledger availability at fixed headroom, and headroom selection with the ledger
present. Their effects should not be merged into one causal attribution.
''' + figures['ablation']+r'''
To connect these cost differences to the objective, write
\begin{equation}
 J=J_{\mathrm{cap}}+J_{\mathrm{sw}},\quad
 J_{\mathrm{cap}}=\sum_{t,i}e_i(t),\quad
 J_{\mathrm{sw}}=\kappa\sum_{a\in\mathcal A_T}\|x_a-e_a^-\|_1.
 \label{eq:costdecomposition}
\end{equation}
Figure~\ref{fig:components} recomputes these terms from the saved per-run
counters. The hatched caps in panel (a) show switching, enlarged separately
in panel (b). They are not additional experiments or newly selected outcomes.
''' + f'''
In P, the ledger variant has mean capacity cost {nominal['capacity_cost']:.2f}
and switching cost {nominal['switching_cost']:.2f}. The no-ledger values are
{noledger['capacity_cost']:.2f} and {noledger['switching_cost']:.3f}.
The capacity difference is {capacity_difference:.2f}, accounting for
{share:.2f}\\% of the total mean cost difference. Thus the nominal saving is
primarily reduced active capacity, not merely reduced switching charges.
''' + r'''
\begin{figure}[!htbp]\centering
\includegraphics[width=.98\linewidth]{cost_components.pdf}
\caption{Post hoc cost decomposition of the frozen ablation runs. Hatched caps denote switching cost.}
\label{fig:components}\end{figure}
The ledger is not uniformly beneficial to deadlines. In L, its class-1 mean
miss fraction is 8.7846\% compared with 3.9807\% without the ledger. Neither
passes the absolute screen, and the ledger uses less capacity. This is a
cost--risk trade-off, not evidence that the ledger is always preferable.
The aggregate counters also do not measure forecast error or explain the
timing of every capacity release. Such mechanisms require per-slot traces.

\subsection{Surrogate feasibility is not deadline reliability}
Define the run-level feasible-decision frequency
\begin{equation}
 \phi=\frac1{N_{\mathrm{ctrl}}}\sum_{t\in\mathcal T_{\mathrm{ctrl}}}
 \mathbf 1\{\max_s\rho_s(x_t,\alpha_t)\le1\},
 \label{eq:feasiblefrequency}
\end{equation}
where $\mathcal T_{\mathrm{ctrl}}$ is the set of control epochs and
$N_{\mathrm{ctrl}}$ its size. Figure~\ref{fig:proxyoutcome} compares the
seed-mean $\phi$ with the worse of the two class seed-mean miss fractions.
This exploratory diagnostic uses existing counters. It is not a calibration
criterion, a prediction-accuracy test, or an event-level correlation analysis.
''' + f'''
The proposed controller declares {diag('P','risk')['feasible_percent']:.2f}\\%
of decisions feasible in P and {diag('M','risk')['feasible_percent']:.2f}\\%
in M, although the worse class mean changes from zero to
{diag('M','risk')['worst_class_mean_percent']:.4f}\\%.
In L, {diag('L','risk')['feasible_percent']:.2f}\\% of decisions remain
surrogate-feasible while the worse class mean reaches
{diag('L','risk')['worst_class_mean_percent']:.4f}\\%.
''' + r'''
The proxy does not encode packet ages, coupled downstream forecasts or an
error budget over the full activation horizon. Consequently, similar values
of $\phi$ can coexist with very different deadline outcomes. Smaller headroom
tightens the score, but it does not repair those omitted state variables.
\begin{figure}[!htbp]\centering
\includegraphics[width=.96\linewidth]{proxy_vs_outcome.pdf}
\caption{Post hoc proxy--outcome diagnostic. Labels identify proposed-policy settings. The dashed line is 0.1\%.}
\label{fig:proxyoutcome}\end{figure}
'''
    # Replace the old results and discussion wholesale, retaining complete data tables.
    app=tex[tex.index(r'\appendix'):]
    # The previous editor moved the reproduction contract ahead of the appendix.
    reproduction=re.search(r'\\section\*\{Reproduction Contract\}.*?(?=\\section\*\{Data and Code Availability\})',tex,re.S)
    if reproduction: app+='\n'+reproduction.group().replace(r'\section*{Reproduction Contract}',r'\section{Reproduction Contract}')
    result=result.replace(r'\subsection{',r'\FloatBarrier'+'\n'+r'\subsection{')
    tex=tex[:tex.index(r'\section{Results}')]+result+'\n\\FloatBarrier\n'+DISC+'\n\\clearpage\n'+app
    tex=tex.replace(r'\usepackage[margin=21mm]{geometry}',r'\usepackage[margin=21mm]{geometry}'+'\n'+r'\usepackage{placeins}')
    tex=tex.replace('physical resource blocks or CPU cycles','physical resource blocks or central processing unit (CPU) cycles')
    # Prevent figures drifting across major argument boundaries. No algorithm
    # style, font, spacing, connector or minipage geometry is changed.
    for sec in ['Related Work and Comparison Boundary','System Model and Problem Definition',
                'Calibrated Action-Aware Controller','Formal Properties and Limits','Experimental Method',
                'Results and Mechanistic Interpretation']:
        tex=tex.replace(r'\section{'+sec+'}',r'\FloatBarrier'+'\n'+r'\section{'+sec+'}')
    assert algorithms(tex)==algs
    receipt=dict(algorithm_sha256=alg_hashes,diagnostics=diagnostics,screen_matrix=gates,
                 nominal_capacity_saving_share_percent=share,source='reliability_results.json',
                 source_sha256=hashlib.sha256((root/'reliability_results.json').read_bytes()).hexdigest(),
                 analysis_status='Post hoc diagnostics. No retuning and no new executions.')
    (out/'substantive_receipt.json').write_text(json.dumps(receipt,indent=2))
    return tex
