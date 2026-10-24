"""Authored manuscript sections for the reliability-screened revision."""

FRONT = r'''
\title{Reliability-Screened Capacity Elasticity under Delayed Telemetry and Actuation: An O-RAN-Motivated Study}
\author{}
\date{}
\begin{document}
\maketitle
\vspace{-12mm}
\begin{abstract}
Resource savings from elastic orchestration can be misleading when they are
obtained by accepting more deadline violations than a fixed-capacity reference.
This study evaluates action-aware elasticity under an explicit, common
reliability screen in an O-RAN-motivated three-stage packet-service model.
A controller projects asynchronously reported queues using applied and pending
actions, then selects capacity and class reservations on a finite grid.
A headroom parameter is selected on separate calibration seeds, using the
same classwise mean-miss target as the comparator families.
The frozen experiment comprises 336 calibration executions and 840 held-out
executions, with twenty independent seeds per test setting. Tests include
periodic, Markov-modulated and compound arrivals, a relocated bottleneck,
degraded telemetry, and constant or variable activation delays.
@@ABSTRACT_RESULT@@
Target-utilization and queue-weighted drift-plus-penalty-inspired adaptations
provide additional diagnostic comparisons, not reproduced O-RAN systems.
@@ABSTRACT_FAILURE@@
The analysis separates finite-grid surrogate optimality, an actuation
irreversibility property, and empirical reliability screening from stochastic
deadline guarantees. All conclusions are limited to synthetic packet-service
experiments, not physical-layer or interoperable O-RAN validation.
\end{abstract}
\noindent\textbf{Keywords:} O-RAN, software-defined networking, delayed actuation,
telemetry, reliability screening, resource elasticity, reproducible simulation.

\section{Introduction}
Open Radio Access Network (O-RAN) exposes programmable control and orchestration
as central system-design concerns \cite{polese}. Software-defined networking
(SDN) separates control decisions from forwarding functions \cite{sdn}, while
virtualization changes how network resources can be provisioned \cite{ecosystem}.
However, a decision does not necessarily take effect when a queue is measured.
A controller may receive a stale report, issue a resource command, and make
another decision before that command becomes active. Accounting only for old
service measurements can then confuse capacity already requested with capacity
still required.

Information age describes the freshness of delivered observations \cite{age}.
Networked control explicitly recognizes sensing and actuation delay
\cite{networked}, and predictive control can incorporate known future actions
\cite{mpc}. These established ideas do not by themselves guarantee a packet
deadline. Nor does a reduction in provisioning cost demonstrate a better
resource allocator if deadline misses increase. This second issue motivates
the central evaluation rule here: a cost advantage is interpreted only after
the compared methods satisfy the same declared reliability screen.

The research question is whether a simple action-ledger projection can reduce
incremental capacity cost while retaining a specified empirical deadline-risk
target, and whether that result survives workload and delay shifts. Two packet
classes traverse access-, transport- and compute-motivated stages. Each stage
uses the same abstract service unit. This is a controlled queueing experiment,
not a physical radio or processor model.

The contributions are fourfold.
\begin{enumerate}
\item A fully specified action-aware finite-grid controller combines a causal
projection with a separately calibrated headroom parameter. Calibration and
test seeds are disjoint, and parameters are not retuned on test outcomes.
\item A common classwise risk screen separates qualified cost comparisons from
raw cost--deadline trade-offs. Fixed provisioning, target-utilization sizing,
and a queue-weighted cost controller are calibrated under that same rule.
\item Seven held-out settings test changes in burst duration, arrival variance,
bottleneck position, telemetry quality and command delay. Both successful and
failed reliability screens are reported, together with component ablations.
\item An executable event contract, independent packet replay, exhaustive
decision checks and record-level reconciliation link the implementation to
the mathematical model and all reported numerical results.
\end{enumerate}
The novelty claim is deliberately limited to this combination and its
controlled evidence. Prediction, autoscaling, drift-plus-penalty control and
reliability-constrained resource allocation are not new in isolation. The
study does not establish a new stability theorem or superiority over deployed
state-of-the-art O-RAN orchestrators.
'''

RELATED_ADDITION = r'''
\subsection{Comparator foundations and delayed optimization}
Kubernetes Horizontal Pod Autoscaling (HPA) uses a ratio between current and
target metrics to recommend replica counts and supports downscale stabilization
\cite{hpa}. The adaptation below borrows target-based sizing and a history
maximum, but changes the resource unit, metric and stabilization duration.
It therefore does not reproduce Kubernetes behavior.
Drift-plus-penalty methods combine a resource penalty with queue-dependent
service rewards \cite{dppenergy}. Their established backlog and convergence
results cannot be transferred to the stale, normalized, multi-stage heuristic
used here. Finally, Delay-Tolerant Constrained Online Convex Optimization
(DTC-OCO) studies multi-slot feedback delay with short- and long-term
constraints and regret bounds \cite{dtc}. Its convex loss-feedback formulation
differs from delayed activation of integer packet-service commands.
DTC-OCO is positioning literature, not an executed baseline. These distinctions
prevent an implementation inspired by a method family from being presented
as a faithful reproduction of a published system.
'''

CALIBRATION_AND_BASELINES = r'''
\subsection{Headroom calibration and reliability screening}
Let $\eta\in\{0.25,0.5,0.75,1\}$ be a dimensionless headroom parameter.
The ratios in the ranking are divided by $\eta$, so smaller values impose a
stricter surrogate-feasibility threshold. They do not impose a hard constraint
on realized packet misses. The control interval, dispersion term and candidate
grid remain fixed across the headroom candidates.

For each policy family $m$ and candidate parameter $\theta$, calibration
estimates the seed mean of each class miss fraction in two report-quality
strata. Let $U_{m\theta cs}$ be its one-sided 95\% percentile-bootstrap upper
endpoint, where $c$ identifies the stratum and $s$ the class. Selection is
\begin{equation}
 \theta_m^*=\arg\min_{\theta\in\Theta_m}
 \overline J_{m\theta}\quad\text{subject to}\quad
 U_{m\theta cs}\le\epsilon\quad\forall c,s,\qquad \epsilon=10^{-3}.
 \label{eq:calibration}
\end{equation}
Here $\overline J$ averages calibration costs across both strata. The threshold
is a 0.1\% seed-mean miss target, not a per-packet chance guarantee or an
O-RAN service-level specification. If a family has no passing candidate, it
is explicitly marked calibration-ineligible and its prespecified conservative
endpoint is retained for diagnosis only. No hidden fallback is substituted
into the proposed policy during a test run.

\subsection{Fixed, target-utilization and queue-weighted comparators}
The fixed family enumerates all sixteen profiles $(0,x_2,x_3)$ on the same
calibration seeds. It starts preprovisioned and retains the earlier drift-based
share controller. It is not an omniscient optimizer, but its known bottleneck
location is used to transpose the selected profile for the compute case.
Consequently, the fixed comparison evaluates complete policies, not the
isolated effect of capacity switching under identical class shares.

The HPA-inspired adaptation computes a target expansion at each expandable
stage using target utilization $u$:
\begin{equation}
 b_i(t)=\left[\left\lceil\frac{\sum_s\bar a_{is}+\sum_s q_{is}/h}{u}
 \right\rceil-\bar c_i\right]_0^3,\qquad
 x_i(t)=\max_{v\in\mathcal H_t}b_i(v).\label{eq:hpa}
\end{equation}
The clipping operator $[z]_0^3$ limits $z$ to $[0,3]$, and $\mathcal H_t$
contains recommendations generated in the last twenty slots. Stage 1 has
zero expansion. Candidate utilizations are $0.55,0.70,0.85,0.95$. Queue
clearance over $h$ slots is a task-specific addition to ratio-based sizing.
The common finite-grid share ranking with $\eta=1$ selects weights for this
fixed target capacity, using the drift projection rather than the action
ledger. This is neither a Kubernetes deployment nor its default timing.

The DPP-inspired adaptation uses a price $v\in\{0.1,0.3,1,3\}$ and selects
the candidate minimizing
\begin{equation}
 v c(x)-\sum_{i,s}\frac{\widetilde q^{L}_{is}+h\bar a_{is}}{D_s}
       \min\{d^{\mathrm{drift}}_{is},g_{is}(\bar c_i+x_i,\alpha)\}.
 \label{eq:dpp}
\end{equation}
Here $\widetilde q^{L}_{is}=[q_{is}+(\Delta_i+L)(\bar a_{is}-\bar\mu_{is})]^+$,
and $d^{\mathrm{drift}}$ replaces the action-aware queue in
\eqref{eq:demand} with that drift projection. Cost breaks objective ties,
followed by share index and enumeration order. Deadline normalization and
clipped service rewards are explicit adaptations. No virtual deadline-deficit
queues, backpressure differentials or imported Lyapunov guarantee are claimed.
A failed calibration for this adaptation is not evidence against the broader
DPP method family.

Two internal ablations complete the comparison. \emph{Uncalibrated} uses the
action ledger with $\eta=1$. \emph{No ledger} uses the selected headroom but
substitutes $\widetilde q^{L}$ for the action-aware projection. The latter
isolates projection effects at a common headroom parameter, not an independently
optimized alternative policy family.

\begin{figure}[htbp]\centering
\begin{minipage}{.96\linewidth}
\textbf{Algorithm 2. Reliability-screened selection and elastic execution}\par\smallskip\hrule\smallskip
\begin{tikzpicture}[x=1cm,y=1cm]
\algline{1}{0}{Input: calibration seeds, parameter grid, $\epsilon$, frozen test settings};
\algline{2}{0}{\textbf{for} each family and candidate parameter \textbf{do}};
\algline{3}{.5}{Execute both calibration strata and compute classwise upper endpoints};
\algline{4}{0}{\textbf{end for}, select minimum-cost passing candidate by (\ref{eq:calibration})};
\algline{5}{0}{Lock selections and record any calibration-ineligible family};
\algline{6}{0}{\textbf{at each elastic control epoch} $t$ \textbf{do}};
\algline{7}{.5}{Read delivered reports, applied ledger and announced activation delay};
\algline{8}{.5}{Project queues with Algorithm 1 and compute $\eta$-scaled ratios};
\algline{9}{.5}{Select the minimum-ranked candidate from all $304$ possibilities};
\algline{10}{.5}{Enqueue the command at $t+L$ without cancellation};
\algline{11}{0}{\textbf{end}, evaluate held-out cost and misses without retuning};
\draw[gray] (.17,-1.16)--(.17,-1.66)--(.35,-1.66);
\draw[gray] (.17,-3.08)--(.17,-4.98)--(.35,-4.98);
\end{tikzpicture}\hrule
\end{minipage}
\end{figure}
'''

IRREVERSIBILITY = r'''
\begin{proposition}[Actuation irreversibility]
Consider two executions with identical exogenous traces, initial states and
all applied actions before slot $a$. A command that first changes an action
at slot $a$ cannot change the on-time-completion indicator of any packet whose
absolute deadline is strictly earlier than $a$.
\end{proposition}
\begin{proof}
The deterministic event contract gives identical packet states and service
decisions through slot $a-1$ by induction. Every completion opportunity up to
the stated packet deadline is therefore identical. A change beginning at
$a$ cannot alter whether the packet completed by an earlier slot.
\end{proof}
In particular, a decision issued at $t$ with activation $t+L$ cannot rescue a
packet with deadline below $t+L$ unless other already-scheduled actions do so.
This structural observation is not a novel stability theorem. It explains why
more accurate accounting of pending actions cannot remove arbitrarily long
actuation latency. Preprovisioning, predictive information before the burst,
or a faster local mechanism is required to change those earlier opportunities.

'''

METHODS = r'''
\section{Experimental Method}
\subsection{Workload, timing and held-out matrix}
Each run has 3340 slots: 300 warm-up slots, a 3000-slot measured birth cohort,
and a forty-slot tail. Background traffic continues during the tail. The class
deadlines are $(15,40)$ slots. An illustrative mapping of twenty milliseconds
per slot gives 300 and 800 milliseconds, not URLLC deadlines. No measured
mapping from packet units to physical resource blocks or CPU cycles is used.

\begin{table}[htbp]\centering\small
\caption{Fixed parameters and complete held-out matrix. Each setting runs six methods on twenty seeds.}
\begin{tabular}{p{31mm}p{116mm}}\toprule
Item & Specification\\\midrule
Common model & Three stages, two classes, $h=5$, $W=20$, $\kappa=0.25$\\
Base capacity & $5+\xi$ per stage, $\xi$ sampled from $(-1,0,0,1)$\\
Periodic bursts & Means $(0.9,2.1)$ outside and $(1.8,3.8)$ inside $t\bmod600\in[180,290)$\\
Capacity stress & Stage 2 capacity $3$ during $t\bmod600\in[170,310)$\\
Initialization & Queue $(0,0)$, ingress $(0.9,2.1)$, service $(2.5,2.5)$, variance $(1,1)$, capacity $5$\\
P & Periodic bursts, transport stress, $(R,p,L)=(3,0.05,10)$\\
M & Markov-modulated Poisson traffic and transport stress, $(3,0.05,10)$\\
B & Markov-modulated batches of three, same conditional means, $(3,0.05,10)$\\
C & Periodic bursts with stress relocated to stage 3, $(3,0.05,10)$\\
R & Periodic transport stress with degraded reports, $(9,0.15,10)$\\
L & Periodic transport stress, long actuation delay, $(3,0.05,50)$\\
J & Periodic transport stress, $(R,p)=(3,0.05)$, announced $L\in\{1,5,10,25,50\}$\\\bottomrule
\end{tabular}\label{tab:settings}
\end{table}

For M and B, a two-state chain begins in the low state. At each slot its
low-to-high probability is 0.005 and its high-to-low probability is 0.02.
Poisson arrival means in each state equal the corresponding nominal and burst
means above. Transport capacity is three in the high state and fluctuating
base capacity in the low state. Other stages retain the exogenous base-capacity
draws. In B, the number of arriving batches is Poisson with mean one third of
the conditional packet rate, and each batch contains three packets. Thus B
preserves conditional means but increases conditional variance. These cases
alter both burst timing and its correlation with transport capacity. They
are synthetic distribution shifts, not independent real-network datasets.

In J, every command delay is sampled uniformly from $\{1,5,10,25,50\}$ and
announced when that command is issued. Controllers do not see future delay
draws. All methods share the same delay sequence within a seed. The mean delay
is 18.2 slots, so P versus J is not a pure variance comparison at equal mean.
Multiple commands can activate in one slot, in issuance order. Commands with
longer delays may activate after subsequently issued commands. They are not
silently canceled or superseded.

\subsection{Frozen selection, equal information and computational budget}
The local protocol, parameter grids and failure rule were written before these
calibration and test executions. It is not an externally registered protocol.
Calibration seeds 12000--12005 are distinct from test seeds 13000--13019.
The two calibration strata are P and R, each at ten-slot actuation delay.
Sixteen fixed profiles plus four candidates for each of the three elastic
families give $(16+4+4+4)\times2\times6=336$ calibration executions.
After selection, seven settings, six methods and twenty seeds give 840 test
executions. All six methods use the same seed-specific exogenous trace, the
same request-index loss flags and one request every five slots. Trace hashes,
admitted cohort counts and delivered-report counts are checked for equality.
Different methods can select different report stages, so payloads need not
be identical. Fixed provisioning has a larger calibration search budget than
each elastic family. Each family has only one selected test configuration.

The prespecified diagnostic fallback parameters are fixed $(3,3)$, headroom
$0.25$, utilization $0.55$ and DPP price $0.1$. They are used only when the
corresponding family has no passing calibration candidate, and that status
remains visible. The earlier 800-run delay-gated study is retained in the
archive as development history. Its seeds and results are not pooled with
the current experiment, and its 1\% calibration target is not reused.

\subsection{Statistical interpretation and qualification rule}
The independent replication unit is a complete seed, not a packet. Results
average seed-level miss fractions and costs. Two-sided 95\% percentile-bootstrap
intervals use 10,000 seed resamples \cite{efron}. One-sided upper endpoints
use the 95th percentile of 10,000 bootstrap means. Paired comparisons resample
within-seed differences. Packet dependence within a run is therefore not
mistaken for thousands of independent trials.

For a proposed-versus-reference comparison in setting $c$, a qualified cost
advantage requires: both families passed calibration, both test upper
endpoints satisfy $U_{cs}\le\epsilon$ for both classes, the upper endpoint
of each paired miss difference is at most $\delta=10^{-3}$, and the upper
endpoint of the paired cost difference is negative. The margin $\delta$ is
0.1 percentage point. This is descriptive noninferiority screening under
common thresholds, not equality of reliability or a guaranteed safety claim.
Internal ablations are displayed as diagnostic comparisons, not separately
calibrated deployment families.

These intervals are unadjusted across settings, classes, candidates and
comparators. No familywise confirmatory significance claim is made. Holm's
procedure \cite{holm} was used for the archived study's separate sign-test
family, not retroactively applied to these bootstrap screens. Calibration
selection and the small six-seed calibration sample can overfit the screen.
Fresh test seeds mitigate reuse of outcomes but do not remove finite-sample
uncertainty or protect against distribution shift.

An all-zero sample gives a zero-width percentile interval. It does not prove
zero risk. With zero seeds exhibiting any miss among twenty independent,
identically distributed test seeds, an exact one-sided 95\% binomial upper
bound for the probability that a whole run exhibits any miss is
$1-0.05^{1/20}=0.1391$. This is a \emph{run-event} bound, not a packet-miss
bound. The all-zero bootstrap result is consequently treated as a descriptive
screen, not a rare-event certificate.

\subsection{Verification and reproducibility}
The release runs 51 unit-test methods, historical-regression checks, an
independent packet replay and complete reconciliation of all 1176 new
execution records. Tests include uncached finite-grid enumeration, constant
delay regression, variable-delay activation order, future-trace exclusion,
compound-arrival construction and independent replay under jitter.
Six selected full test runs are regenerated and compared exactly to saved
records. Mathematical cost definitions include every applied command change,
including multiple changes within a slot. Tables and vector plots are built
directly from execution JSON. The final PDF is compiled to resolved references
and checked separately from its intermediate build passes.
'''

RESULTS = r'''
\section{Results}
\subsection{Calibration outcome and its limits}
@@CALIBRATION_NARRATIVE@@
\begin{figure}[htbp]\centering
\includegraphics[width=.96\linewidth]{calibration.pdf}
\caption{Calibration cost and worst class/stratum upper endpoint. Each marker
represents one candidate evaluated on twelve runs. The horizontal line is the
0.1\% screening target. Points below the display floor represent zero empirical
endpoints, not certified zero risk.}
\label{fig:calibration}
\end{figure}
Calibration eligibility is not a monotonic ranking of policy quality. A family
may pass on six seeds and fail on twenty fresh seeds, or satisfy the target
with unnecessarily high resource cost. The selected parameters therefore
remain fixed through every held-out setting.

\subsection{Common-target cost comparison}
Table~\ref{tab:qualified} gives the proposed-versus-fixed comparison, including
both class upper endpoints and the paired cost interval. A cost reduction
without passing the qualification rule is labeled unqualified, even if its
cost interval is entirely below zero.
@@QUALIFIED_TABLE@@
@@PRIMARY_NARRATIVE@@
\begin{figure}[htbp]\centering
\includegraphics[width=.98\linewidth]{reliability_primary.pdf}
\caption{Held-out costs and deadline-miss percentages with unadjusted 95\%
seed-bootstrap intervals. P, M, B, C, R, L and J are defined in
Table~\ref{tab:settings}. The 0.1\% dashed line is the common target.
The DPP-inspired adaptation is calibration-ineligible and diagnostic only.}
\label{fig:primary}
\end{figure}

\subsection{Distribution shift and activation-delay failures}
@@SHIFT_NARRATIVE@@
These outcomes distinguish successful local calibration from robust deployment.
In particular, unseen burst timing, larger arrival batches and long activation
delays cannot be certified by a screen fitted only to periodic ten-slot cases.
The model does not include an online safety override. Its negative outcomes
are retained rather than replaced by an oracle fixed policy.
\begin{figure}[htbp]\centering
\includegraphics[width=.94\linewidth]{qualified_cost.pdf}
\caption{Paired cost differences, proposed minus fixed. Green denotes a
comparison satisfying the entire descriptive qualification rule. Gray denotes
an unqualified comparison, regardless of the direction of its cost difference.
Intervals are unadjusted 95\% paired-bootstrap intervals.}
\label{fig:qualified}
\end{figure}

\subsection{Action-ledger and headroom ablations}
@@ABLATION_NARRATIVE@@
\begin{figure}[htbp]\centering
\includegraphics[width=.96\linewidth]{reliability_ablation.pdf}
\caption{Component ablations on identical test seeds. The uncalibrated controller
uses $\eta=1$. The no-ledger controller retains selected headroom but uses a
drift projection. The error bars describe seed-mean uncertainty, not predictive
confidence bounds for the controller.}
\label{fig:ablation}
\end{figure}
The comparison does not demonstrate that an action ledger is universally
beneficial. It isolates its contribution for one proxy, one calibrated headroom
and the tested workloads. Shared stage weights, uncoupled downstream forecasts
and absent packet-age telemetry remain important limitations.
'''

DISCUSSION = r'''
\section{Discussion and Threats to Validity}
\subsection{What the evidence establishes}
The study improves the interpretability of an elasticity comparison by making
the reliability screen explicit before interpreting cost. The relevant result
is not simply lower mean resource usage. It is lower paired cost in a setting
where both complete policies pass the declared classwise test screen and the
paired miss-margin screen. Cases failing any part of that definition remain
cost--risk trade-offs or outright failures. The qualification rule is useful
for auditability even when it rejects a favorable-looking cost result.

The action ledger adds information that a rate-only forecast omits: known
changes already applied or awaiting activation. It does not reveal future
traffic, future base capacities or undisclosed activation delays. The projection
holds reported capacity and mean ingress fixed and treats stages independently.
An upstream action can alter downstream ingress in ways that this projection
cannot foresee. Fluid borrowing also lacks the packet-age information used
by the actual local scheduler. These approximations explain why finite-grid
surrogate feasibility must not be relabeled deadline feasibility.

\subsection{Statistical and comparator limitations}
Six calibration seeds per stratum and twenty test seeds per setting provide
limited evidence for a 0.1\% target. Percentile intervals are especially weak
when all seed outcomes are zero, and multiple candidate screens are not
simultaneously calibrated. Larger independent experiments and rare-event
methods would be needed for operational reliability claims. The two-state
traffic construction and the selected compound batch size cover only narrow
forms of distribution shift. No adversarial worst-case envelope is established.

The additional comparators are transparent adaptations, not faithful
implementations of Kubernetes HPA, a published O-RAN system or a theorem-backed
deadline-constrained DPP controller. Their calibration failures restrict what
can be concluded from their cost and miss curves. The fixed policy starts
preprovisioned, knows the stressed domain and retains its own share controller.
That makes it a meaningful complete-policy reference but prevents attribution
of every difference solely to capacity elasticity. An ideal future comparison
would reproduce competitive published methods in their native validated model.

\subsection{O-RAN interpretation and remaining validation}
The access/transport/compute interpretation motivates cross-domain delayed
orchestration, but no E2, A1 or O1 messages are implemented. Radio channel
variation, physical resource blocks, retransmissions, numerology, processor
execution times, virtualization interference and network topology are absent.
Uniform one-unit packet service cannot stand in for calibrated radio and CPU
resources. Abstract incremental cost is not energy, monetary expenditure or
measured operational cost.

A practical follow-on would integrate the action ledger with an actual RIC
or orchestration interface, measure telemetry and activation latency, map
capacity to service curves, and repeat the frozen comparison with recorded
traffic and independently implemented baselines. The platforms discussed in
Section 2 provide possible routes, but none was run here.

\section{Conclusion}
Delayed resource orchestration requires separate treatment of requested
capacity, activated capacity and observed queue state. This paper combines
an action-aware projection with independently calibrated headroom and evaluates
it under an explicit common reliability screen. The completed synthetic study
contains 336 calibration and 840 held-out executions, including distribution
shift, degraded reports, variable actuation and component ablations.
@@CONCLUSION_RESULT@@
The finite-grid and event-contract analysis establishes limited implementation
properties, not stochastic deadline guarantees. The main finding is therefore
conditional: action-aware elasticity can yield a qualified resource advantage
in particular tested regimes, while reliability screening exposes regimes in
which the same policy should not be claimed as an improvement. Physical O-RAN
validation and reproduced competitive systems remain necessary before making
deployment or state-of-the-art claims.

\section*{Data and Code Availability}
The accompanying archive contains the simulator, frozen protocol, all
calibration and held-out seed records, selected parameters, verification tests,
manuscript sources and vector figures. It also retains historical experiments
without pooling them into the current results. No external dataset was used
and no public repository or archival DOI is asserted.

\clearpage
\appendix
\section{Complete Held-Out Results}
@@FULL_TABLE@@
\clearpage
\section{Complete Paired Comparisons}
@@PAIRED_TABLE@@
\section{Reproduction Contract}
Run \texttt{python reliability\_study.py} to reproduce the calibration and
held-out matrix. Existing complete checkpoints are reused only if the frozen
protocol hash matches. Remove or relocate those specific checkpoint files
to execute all runs anew. Run \texttt{python verify\_reliability.py} to reconcile
all metrics and selected deterministic replays, followed by
\texttt{python build\_reliability\_paper.py} and
\texttt{python build\_release.py}. The archive includes the exact dependency
versions and checksums. The PDF is generated from saved results, not from
hand-entered headline numbers. Reproduction establishes consistency of this
synthetic experiment, not external validity for a physical network.
'''
