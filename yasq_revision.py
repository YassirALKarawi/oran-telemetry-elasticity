"""YASQ manuscript revision. Uses existing frozen results without retuning."""
import re

ABSTRACT = r'''Resource elasticity under delayed telemetry can reduce provisioning cost while increasing deadline violations. This study examines that trade-off in an Open Radio Access Network (O-RAN)-motivated, three-stage service chain. A causal controller projects reported queues using applied actions and pending commands, then selects capacity and class reservations on a finite grid. A headroom parameter is calibrated separately under a common classwise mean-miss target of 0.1\%. The experiment comprises 336 calibration and 840 held-out executions across seven settings, with twenty independent test seeds per setting. Comparisons include fixed capacity, target-utilization sizing, a queue-weighted cost controller and component ablations. Three fixed-reference comparisons satisfy the complete descriptive reliability screen and reduce mean incremental cost by 35.61--37.73\%. Markov-modulated traffic, compound arrivals and fifty-slot actuation expose failures of the selected policy. Derived sensitivity relations explain how headroom and demand uncertainty affect surrogate feasibility, while paired intervals quantify observed cost differences. The results establish conditional advantages within a synthetic packet-service model. They do not certify rare-event reliability or validate a physical O-RAN implementation.'''

DERIVATION = r'''
\subsection{From queue workload to the feasibility surrogate}
For a fixed report state, define the unscaled service-time proxy
\begin{equation}
 H_s(x,\alpha)=\sum_{i=1}^{3}\frac{d_{is}}{\widetilde g_{is}},
 \qquad \widetilde g_{is}=\max\{10^{-3},g_{is}(\bar c_i+x_i,\alpha)\}.
 \label{eq:worktime}
\end{equation}
The quantity $\widetilde g_{is}$ is the floored reservation denominator used
in the implemented ranking. Dividing packet workload $d_{is}$ by reserved
packets per slot gives a stage service-time proxy. Adding the stage proxies
gives $H_s$ in slots. This algebra does not incorporate the packet ages or
joint stage dynamics required for a true end-to-end delay bound. The controller
normalizes this proxy by the headroom-adjusted deadline:
\begin{equation}
 \rho_s=\frac{H_s}{\eta D_s},\qquad
 \mathcal F(\eta)=\{(x,\alpha)\in\mathcal X:H_s(x,\alpha)\le\eta D_s\ \forall s\}.
 \label{eq:feasibleset}
\end{equation}
For the same reports and candidate actions, $0<\eta_1\le\eta_2$ implies
$\mathcal F(\eta_1)\subseteq\mathcal F(\eta_2)$. Thus reducing $\eta$ cannot
create a newly feasible candidate at that decision state. If both sets are
nonempty, the minimum feasible proxy cost cannot decrease when $\eta$ is
reduced. This local statement does not imply monotone realized cost over a
closed-loop run, where actions also change future reports and queues.

Holding the projected state and reservations fixed, the corresponding local
sensitivities are
\begin{align}
 \frac{\partial\rho_s}{\partial\eta}&=-\frac{\rho_s}{\eta},&
 \frac{\partial\rho_s}{\partial\widehat q_{is}}&=\frac{1}{\eta D_s\widetilde g_{is}},
 \label{eq:etasensitivity}\\
 \frac{\partial\rho_s}{\partial v_{is}}&=
 \frac{\sqrt h}{2\eta D_s\widetilde g_{is}\sqrt{v_{is}}},\qquad v_{is}>0.
 \label{eq:variancesensitivity}
\end{align}
These derivatives describe the score between changes in integer reservations.
They are not derivatives of the selected action, which can jump between grid
points. Equation~\eqref{eq:etasensitivity} explains why headroom can exclude
cheap candidates, while \eqref{eq:variancesensitivity} identifies the greater
sensitivity associated with small reservations and short deadlines. At zero
variance the square-root term is continuous but its derivative is not finite.
'''

MECHANISM = r'''
\subsection{Connecting the curves to the model}
Figure~\ref{fig:primary} separates paid expansion $J$ from the two observed
miss fractions $V_0$ and $V_1$. The cost component in \eqref{eq:proxycost}
encourages low expansion whenever the score admits a feasible candidate.
Reducing $\eta$ tightens \eqref{eq:feasibleset}, which explains the resource
increase seen in the headroom sweep. The packet outcomes still depend on the
actual sequence of service opportunities, so the fitted score alone cannot
explain a reliability improvement without the measured $V_s$ values.

For the compound-arrival experiment, let $K_s$ be Poisson with mean
$\lambda_s/b$, where $\lambda_s$ is the conditional class arrival rate and
$b=3$ is the batch size. Then $A_s=bK_s$ has
\begin{equation}
 \mathbb E[A_s\mid\lambda_s]=\lambda_s,\qquad
 \operatorname{Var}(A_s\mid\lambda_s)=b\lambda_s.
 \label{eq:batchmoments}
\end{equation}
Thus B changes conditional arrival variance even when its conditional mean
matches the Markov case M. This is consistent with greater queue excursions,
but the controller uses reported \emph{net-flow} variance $v_{is}$ rather than
the analytical arrival variance in \eqref{eq:batchmoments}. The two variances
must not be equated. The observed classwise differences also depend on
reservations, borrowing and bottleneck location.

Figure~\ref{fig:qualified} conditions the interpretation of negative paired
cost differences on the complete risk screen. In L, $L=50$ exceeds both
$D_0=15$ and $D_1=40$. A command issued when a burst is detected cannot alter
service opportunities before its activation. The actuation irreversibility
property therefore provides a structural explanation for the failure regime,
without asserting that every packet must miss. Figure~\ref{fig:ablation}
then distinguishes the effects of $\eta$ and the ledger under matched traces.
'''

def revise(tex, sensitivity_table):
    tex=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:r'\begin{abstract}'+'\n'+ABSTRACT+'\n'+r'\end{abstract}',tex,flags=re.S)
    tex=tex.replace('Drift-plus-penalty methods combine','Drift-plus-penalty (DPP) methods combine')
    tex=tex.replace('not URLLC deadlines','not ultra-reliable low-latency communication (URLLC) deadlines')
    # The first CPU occurrence precedes the experiment section.
    tex=tex.replace('No calibrated CPU or physical radio model','No calibrated central processing unit (CPU) or physical radio model')
    tex=tex.replace('packet capacity, not xApp deployment','packet capacity, not xApp deployment')
    tex=tex.replace('orchestration and sharing of\nxApp-based services','orchestration and sharing of\nnear-real-time control applications (xApps)')
    tex=tex.replace('an oracle fixed policy','a retrospectively selected fixed policy')
    tex=tex.replace('no E2, A1 or O1 messages are implemented','standard O-RAN interface messages are not implemented')
    tex=tex.replace('The set $\\mathcal A_T$ contains',
                    'The norm $\\lVert z\\rVert_1=\\sum_i|z_i|$ sums componentwise expansion changes for a vector $z$. The set $\\mathcal A_T$ contains')
    tex=tex.replace('is not an omniscient optimizer','does not use future traffic')
    tex=tex.replace('The domain labels are an O-RAN motivation, not implemented protocol entities.}',
                    'The domain labels provide the O-RAN interpretation of the queueing model.}')
    tex=tex.replace(r'\subsection{State, service and event order}',
        r'\subsection{State, service and event order}'+'\n'+r'Figure~\ref{fig:architecture} identifies the controlled stages and information paths. Table~\ref{tab:notation} summarizes the principal symbols and units.'+'\n')
    tex=tex.replace(r'\caption{Notation and units. All capacities and workloads are abstract.}',
                    r'\caption{Notation and units. All capacities and workloads are abstract.}\label{tab:notation}')
    tex=tex.replace('A decision at time $t$ creates an immutable command',
        r'Figure~\ref{fig:timeline} relates measurement age, report delivery and command activation. A decision at time $t$ creates an immutable command')
    tex=tex.replace(r'\subsection{Headroom calibration and reliability screening}',DERIVATION+r'\subsection{Headroom calibration and reliability screening}')
    tex=tex.replace(r'\theta_m^*=\arg\min',r'\theta_m^*=\arg\min')
    tex=tex.replace(r'Here $\overline J$ averages calibration costs across both strata.',
        'The finite set $\\Theta_m$ contains the candidate parameters for family $m$. Here $\\overline J$ averages calibration costs across both strata.')
    tex=tex.replace(r'\subsection{Common-target cost comparison}',sensitivity_table+r'\subsection{Common-target cost comparison}')
    tex=tex.replace(r'\section{Discussion and Threats to Validity}',MECHANISM+r'\section{Discussion and Threats to Validity}')
    tex=tex.replace(r'\section{Conclusion}',r'\clearpage'+'\n'+r'\section{Conclusion}')
    availability=re.search(r'\\section\*\{Data and Code Availability\}.*?(?=\\clearpage\s*\\appendix)',tex,re.S)
    if availability:
        block=availability.group(0)
        tex=tex[:availability.start()]+tex[availability.end():]
        tex+='\n'+block
    tex=tex.replace(r'\section{Complete Held-Out Results}',r'\section{Complete Held-Out Results}'+'\n'+r'Table~\ref{tab:allresults} reports every method and setting using the same classwise metrics.'+'\n')
    tex=tex.replace(r'\section{Complete Paired Comparisons}',r'\section{Complete Paired Comparisons}'+'\n'+r'Table~\ref{tab:allpaired} reports cost and miss differences for every comparator.'+'\n')
    tex=tex.replace('draw,rounded corners=2pt,align=center','draw=blue!45!black,line width=.7pt,rounded corners=2pt,align=center')
    # Link the related-work table and avoid unreferenced display objects.
    tex=tex.replace(r'\subsection{Comparator foundations and delayed optimization}',
        r'Table~\ref{tab:related} summarizes the scope differences that determine which comparisons are meaningful.'+'\n'+r'\subsection{Comparator foundations and delayed optimization}')
    return tex

def unsplit(lines,label):
    """Convert the two known one-page appendix tables to nonbreaking floats."""
    spec=re.search(r'\\begin\{longtable\}(\{[^}]+\})',lines[0]).group(1)
    caption=lines[1][:-2] if lines[1].endswith('\\\\') else lines[1]
    head=lines[2].replace(r'\endfirsthead','')
    body=lines[5:-1]
    return '\n'.join([r'\begin{table}[!htbp]\centering\footnotesize',caption+r'\label{'+label+'}',
                       r'\begin{tabular}'+spec,head,*body,r'\bottomrule\end{tabular}\end{table}'])
