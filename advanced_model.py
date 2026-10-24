"""Exact analytical enrichment of the unchanged packet-service experiment."""
from yasq_quality import algorithms

AGE = r'''
\subsection{Age-resolved state and exact deadline accounting}
Queue length alone does not identify the number of packets approaching their
deadline. Introduce $X_{isa}(t)$, the number of class-$s$ packets at stage $i$
whose age is $a=t-b$, measured after external arrivals and before service in
slot $t$. Let $Y_{isa}(t)$ count the packets of that age served at that stage
in that slot. Both variables are nonnegative integers. This representation
retains the birth timestamps already present in the simulator and does not
add a new measurement to the controller. Its aggregation is
\begin{equation}
 B_{is}(t)=\sum_{a\ge0}X_{isa}(t),\qquad
 S_{is}(t)=\sum_{a\ge0}Y_{isa}(t),\qquad
 0\le Y_{isa}(t)\le X_{isa}(t).
 \label{eq:ageaggregate}
\end{equation}
Here $B_{1s}=Q_{1s}+A_s$ and $B_{is}=Q_{is}$ for $i>1$, consistent with the
earlier pre-arrival queue convention. With initially empty queues, the exact
age dynamics are
\begin{align}
 X_{1s,0}(t+1)&=A_s(t+1),&X_{is,0}(t+1)&=0\quad(i>1),\label{eq:agebirth}\\
 X_{1s,a+1}(t+1)&=X_{1sa}(t)-Y_{1sa}(t),\label{eq:agefirst}\\
 X_{is,a+1}(t+1)&=X_{isa}(t)-Y_{isa}(t)+Y_{i-1,s,a}(t),
 \quad i=2,3.\label{eq:agetransit}
\end{align}
All survivors age by one slot. Upstream departures become downstream work
for the next slot because service is executed in reverse stage order.
Summing these equations over age recovers the aggregate queue recurrences.
In particular, no packet can traverse two stages in a single slot.

The service constraints combine the stage budget with within-class FIFO:
\begin{align}
 \sum_{s,a}Y_{isa}(t)&=\min\!\left\{C_i(t),\sum_{s,a}X_{isa}(t)\right\},
 \label{eq:agebudget}\\
 Y_{isa}(t)>0&\ \Longrightarrow\
 \sum_{v>a}\bigl[X_{isv}(t)-Y_{isv}(t)\bigr]=0.
 \label{eq:agefifo}
\end{align}
Equation~\eqref{eq:agefifo} requires every older packet of the same class to
be served before a younger age group receives service. Between classes,
reserved quotas and earliest-deadline borrowing still determine the totals
$S_{is}$ through the scheduler already specified. Thus
\eqref{eq:agebudget}--\eqref{eq:agefifo} are necessary service constraints,
not a replacement scheduling optimization with freely selectable departures.
Late packets remain queued and consume service. Truncating all ages at $D_s$
would therefore change the model.

Let $\chi(t,a)=\mathbf1\{b_{\min}\le t-a<b_{\max}\}$ identify the measured
birth cohort, with $b_{\min}=300$ and $b_{\max}=3300$. The indicator
$\mathbf1\{\cdot\}$ is one when its condition holds and zero otherwise.
For $N_s>0$, the deadline-miss fraction has the equivalent exact expression
\begin{equation}
 V_s=1-\frac1{N_s}\sum_{t=0}^{T-1}\sum_{a=0}^{D_s-1}
 \chi(t,a)Y_{3sa}(t),\qquad
 N_s=\sum_{t=b_{\min}}^{b_{\max}-1}A_s(t).
 \label{eq:agemiss}
\end{equation}
When $N_s=0$, set $V_s=0$. Completion latency is $a+1$, so the upper limit
$D_s-1$ includes completion exactly at the deadline. Every cohort packet
contributes once to either the on-time count or its complement. The tail
extends beyond all cohort deadlines, making that complement identical to
late completions plus unfinished packets in \eqref{eq:miss}.

This identity also exposes an information loss in the workload proxy. Two
states with the same $B_{is}$ and service reservations can have different
$X_{isa}$ and hence different attainable on-time counts. At the last stage,
one packet of age $D_s-1$ can still finish on time if served immediately,
whereas a packet of age $D_s$ cannot. Their queue lengths are identical.
Aggregate feasibility therefore cannot be sufficient for deadline feasibility
without additional age information or assumptions.
'''

ACT = r'''
\subsection{Command-indexed actuation and switching geometry}
Index issued commands by $k$, with issue slot $t_k$, announced delay $L_k$,
activation slot $d_k=t_k+L_k$, expansion $x_k$ and stage-weight matrix $W_k$.
In the proposed controller, each row of $W_k$ is
$(\alpha_k,1-\alpha_k)$. Let command $k=0$ denote the initialized action,
with an activation time before the run. The action active after all due
commands in slot $t$ is characterized by
\begin{equation}
 k^*(t)=\underset{k:d_k\le t}{\arg\max}_{\rm lex}(d_k,k),
 \qquad e(t)=x_{k^*(t)},\qquad W(t)=W_{k^*(t)}.
 \label{eq:activecommand}
\end{equation}
The lexicographic maximum first selects the latest activation time and then
the latest issue index among simultaneous activations. It is not the latest
issue index across all commands. Consequently, an older command with a larger
delay can overwrite a newer command that became active earlier.

For the ordered list of commands activating in slot $t$, write
$\mathcal K_t=(k_{t,1},\ldots,k_{t,n_t})$, ordered by issue index. Define
$e^{t,0}=e(t-1)$ and $e^{t,j}=x_{k_{t,j}}$ for $j\ge1$, using the initialized
expansion for $e(-1)$. The exact per-slot and full-run costs are
\begin{align}
 j_t&=\sum_i e_i(t)+\kappa\sum_{j=1}^{n_t}
       \|e^{t,j}-e^{t,j-1}\|_1,\label{eq:slotcost}\\
 J&=\sum_{t=0}^{T-1}j_t.\label{eq:commandsumcost}
\end{align}
An empty activation list contributes zero switching cost. The triangle
inequality gives
\begin{equation}
 \sum_{j=1}^{n_t}\|e^{t,j}-e^{t,j-1}\|_1
 \ge\|e(t)-e(t-1)\|_1.
 \label{eq:switchlower}
\end{equation}
Thus charging only the net slot change is a lower bound on the implemented
switching charge. For example, simultaneous changes
$(0,0,0)\rightarrow(0,3,0)\rightarrow(0,0,0)$ incur six switching units,
or cost $1.5$ at $\kappa=0.25$, although the net change is zero.
This distinction matters in J, where multiple commands can activate together.
Equations~\eqref{eq:activecommand}--\eqref{eq:switchlower} explain why a
penalty relative to the previous requested action cannot equal realized
switching cost in every execution.
'''

INFO = r'''
\subsection{Augmented state and the causal policy restriction}
The packet and command descriptions can be combined into a state
\begin{equation}
 Z_t=\bigl(X_t,e_t,W_t,\mathcal P_t,\mathcal R_t,\mathcal D_t,
           \mathcal H_t^{\rm meas},\zeta_t\bigr).
 \label{eq:augmentedstate}
\end{equation}
Here $X_t$ collects all age bins, $\mathcal P_t$ stores issued commands awaiting
activation, $\mathcal R_t$ stores reports awaiting delivery, and
$\mathcal D_t$ stores the latest accepted report from each stage.
$\mathcal H_t^{\rm meas}$ contains the finite measurement histories, and
$\zeta_t$ contains the exogenous traffic/capacity state and periodic phase
needed for the selected workload law. State-dependent report construction and
the event order define a transition map
\begin{equation}
 Z_{t+1}=\mathcal F_t(Z_t,u_t,\xi_{t+1}),\qquad
 u_t=\pi_t(\mathcal I_t),\quad\pi\in\Pi_{\mathcal I}.
 \label{eq:causaltransition}
\end{equation}
The random input $\xi_{t+1}$ accounts for exogenous evolution, report loss and
any future announced delays. The action $u_t$ specifies the requested command
and the stage selected for telemetry, and is null outside control epochs.
The information $\mathcal I_t$ consists of delivered reports and their
timestamps, the applied ledger, previously issued commands and the current
announced delay. The set $\Pi_{\mathcal I}$ contains policies measurable with
respect to this information. It excludes access to the hidden age bins and
undelivered reports, even though the simulator retains them for execution.

The objective in \eqref{eq:ideal}, together with
\eqref{eq:agebirth}--\eqref{eq:agemiss} and
\eqref{eq:activecommand}--\eqref{eq:causaltransition}, is therefore a
partially observed, integer-valued sequential resource-allocation problem.
The actual controller compresses $\mathcal I_t$ into projected queue lengths
and a finite-grid score. That compression retains known action effects but
discards the full age distribution and uncertain future arrivals. The expanded
formulation characterizes the underlying problem. The executed algorithm
continues to solve its stated per-decision surrogate, without an additional
stochastic optimizer or an unreported computational benchmark.
'''

CUT = r'''
\subsection{Residual-deadline cuts and unavoidable misses}
Age resolution sharpens the aggregate capacity obstruction. At a pre-service
slot $t$, consider measured-cohort packets currently waiting at stages
$j\le i$ whose absolute deadlines are no later than $d$, with $t\le d<T$.
Their count is
\begin{equation}
 B_i^{\mathcal C}(t,d)=
 \sum_{j=1}^{i}\sum_{s,a}
 \chi(t,a)\mathbf1\{t-a+D_s-1\le d\}X_{jsa}(t).
 \label{eq:deadlinedemand}
\end{equation}
Every such packet still needs stage-$i$ service. Because the remaining
$3-i$ stages each require a later slot, it must leave stage $i$ no later
than $d-(3-i)$. Even if all available service were assigned to these packets,
their on-time completion count cannot exceed
\begin{equation}
 K_i(t,d)=\sum_{u=t}^{d-(3-i)}C_i(u),
 \label{eq:deadlinecapacity}
\end{equation}
with an empty sum interpreted as zero. Let $M^{\mathcal C}(t,d)$ denote the
eventual number of misses among currently queued cohort packets with deadline
at most $d$. The necessary pathwise inequality is
\begin{equation}
 M^{\mathcal C}(t,d)\ge
 \max_{i\in\{1,2,3\}}[B_i^{\mathcal C}(t,d)-K_i(t,d)]^+.
 \label{eq:misscut}
\end{equation}
To prove the inequality, each on-time packet in the stage-$i$ subset must
consume one distinct service unit in its stated window. At most $K_i$ such
units exist, leaving at least $[B_i^{\mathcal C}-K_i]^+$ misses. The maximum
combines valid lower bounds without counting the same packet multiple times.
The bound relaxes upstream release times, other traffic and reserved shares,
so a zero value does not establish feasibility. Unlike a steady-state load
condition, it retains residual deadlines and downstream transit time.

For the constant-delay cases, no command issued at or after $t$ changes
capacity before $t+L$. Let $e_i^{\rm pend}(u)$ be the expansion obtained by
replaying the applied action and commands already issued before $t$, and let
$e_i^{\max}$ be $0$ for stage 1 and $3$ otherwise. A control-independent upper
envelope on capacity opportunities is
\begin{equation}
 \overline K_i(t,d)=\sum_{u=t}^{d-(3-i)}
 \left[c_i(u)+
 \begin{cases}
 e_i^{\rm pend}(u),&u<t+L,\\
 e_i^{\max},&u\ge t+L.
 \end{cases}\right].
 \label{eq:delaycut}
\end{equation}
Since $K_i\le\overline K_i$, substituting $\overline K_i$ into
\eqref{eq:misscut} gives a lower bound valid for every subsequent admissible
control sequence under that fixed-delay assumption. Future base capacities
are not observed by the controller, so this is a pathwise analytical bound,
not an implemented online certificate. In J, later-issued commands can have
shorter delays. The fixed-$L$ envelope must not be applied to that case.
'''

def enrich(tex):
    before=algorithms(tex)
    tex=tex.replace(r'\subsection{Telemetry and immutable commands}',AGE+r'\subsection{Telemetry and immutable commands}')
    tex=tex.replace(r'\subsection{Objective and measured reliability}',ACT+r'\subsection{Objective and measured reliability}')
    # The age representation refers forward to cost/miss definitions through labels.
    tex=tex.replace(r'\FloatBarrier'+'\n'+r'\section{Calibrated Action-Aware Controller}',INFO+r'\FloatBarrier'+'\n'+r'\section{Calibrated Action-Aware Controller}')
    tex=tex.replace(r'\subsection{Capacity obstruction and computational cost}',CUT+r'\subsection{Capacity obstruction and computational cost}')
    assert algorithms(tex)==before
    assert all(r'\label{'+x+'}' in tex for x in ['eq:agemiss','eq:activecommand','eq:causaltransition','eq:misscut','eq:delaycut'])
    return tex
