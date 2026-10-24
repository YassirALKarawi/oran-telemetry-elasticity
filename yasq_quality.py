"""Substantive YASQ refinement. Algorithm display blocks are immutable."""
import re

ARCH = r'''\begin{figure}[htbp]\centering
\begin{tikzpicture}[>=Stealth,x=1cm,y=1cm,font=\small,
 box/.style={draw=blue!45!black,line width=.7pt,rounded corners=2pt,align=center,minimum height=12mm,text width=37mm},
 info/.style={->,blue!65!black,dashed},act/.style={->,orange!65!black}]
\node[box] (r) at (0,0) {Delivered reports\\$r_i$, timestamp $\tau_i$};
\node[box] (c) at (5,0) {Projection and ranking\\$\widehat q$, $\eta$, 304 candidates};
\node[box] (l) at (10,0) {Action memory\\applied $\mathcal L$, pending $\mathcal P$};
\draw[->] (r)--(c);
\draw[->] (c.east)--node[above,font=\scriptsize]{issue}(l.west);
\draw[->] (l.north)--++(0,.65)-|node[pos=.25,above,font=\scriptsize]{known action trajectory}(c.north);
\node[box] (s1) at (0,-3.1) {Access-motivated stage\\$Q_{1s}$, $e_1=0$};
\node[box] (s2) at (5,-3.1) {Transport-motivated stage\\$Q_{2s}$, $e_2\in\{0,1,2,3\}$};
\node[box] (s3) at (10,-3.1) {Compute-motivated stage\\$Q_{3s}$, $e_3\in\{0,1,2,3\}$};
\draw[->,thick] (s1)--node[above,font=\scriptsize]{$S_{1s}$}(s2);
\draw[->,thick] (s2)--node[above,font=\scriptsize]{$S_{2s}$}(s3);
\draw[info] (-1,-2.5)--(-1,-.6);
\draw[blue!65!black,dashed] (-1,-2.1)--(9,-2.1);
\draw[blue!65!black,dashed] (4,-2.5)--(4,-2.1);
\draw[blue!65!black,dashed] (9,-2.5)--(9,-2.1);
\node[font=\scriptsize,fill=white] at (3,-2.1) {one selected snapshot every $h$ slots, delay $R$, loss $p$};
\draw[orange!65!black] (11,-.6)--(11,-1.3)--(1,-1.3);
\foreach \x in {1,6,11}{\draw[act] (\x,-1.3)--(\x,-2.5);}
\node[font=\scriptsize,fill=white] at (5,-1.3) {activation at $t+L$: all stage shares, expandable capacities};
\node[align=center,font=\scriptsize] at (5,-4.1) {Solid black: packet flow\quad Dashed blue: telemetry\quad Orange: applied commands\\Domain labels are abstractions, not implemented O-RAN interfaces.};
\end{tikzpicture}
\caption{Closed-loop information and actuation paths across all three service stages.}
\label{fig:architecture}\end{figure}'''

TIME = r'''\begin{figure}[htbp]\centering
\begin{tikzpicture}[>=Stealth,x=1cm,y=1cm,font=\small]
\draw[->,thick] (0,0)--(13.5,0) node[right]{slot};
\foreach \x/\lab in {0.6/{$\tau_i$},3.3/{$\tau_i+R$},6/{$t$},12.4/{$t+L$}}{
 \draw (\x,.12)--(\x,-.12) node[below=2mm]{\lab};}
\node[above,align=center] at (.6,.25){snapshot};
\node[above,align=center] at (3.3,.25){delivery};
\node[above,align=center] at (6,.25){decision};
\node[above,align=center] at (12.4,.25){activation};
\draw[<->,blue!65!black] (.6,-.9)--node[below]{report age $\Delta_i$}(6,-.9);
\draw[<->,orange!65!black] (6,-.9)--node[below]{announced delay $L$}(12.4,-.9);
\draw[line width=1.3pt,blue!65!black] (.6,1.25)--(6,1.25);
\draw[line width=1.3pt,orange!65!black] (6,1.25)--(12.4,1.25);
\node[above,font=\scriptsize] at (3.3,1.25){replay applied ledger};
\node[above,font=\scriptsize] at (9.2,1.25){replay known pending commands};
\foreach \x in {8,10.3}{\draw[->,orange!65!black] (\x,2.2)--(\x,1.35);}
\node[above,font=\scriptsize] at (9.15,2.2){earlier-issued commands activate};
\node[align=center,font=\scriptsize] at (6.5,-2){Project to the pre-service state at $t+L$.\\The newly selected command affects service, not this projected state.};
\end{tikzpicture}
\caption{Projection horizon and causal boundary. Positions are schematic, not measured delays.}
\label{fig:timeline}\end{figure}'''

BRIDGE = r'''
\subsection{Information-constrained design and implemented approximation}
Let $\mathcal I_t$ contain only delivered reports, previously issued commands,
the applied ledger, and the current announced activation delay. A causal policy
$\pi$ maps this information to a command. Let $\Pi$ be the class of such policies
respecting the finite capacity and share grids. For a specified workload law,
the design objective can be written as
\begin{equation}
 \inf_{\pi\in\Pi}\mathbb E_\pi[J]
 \quad\text{subject to}\quad\mathbb E_\pi[V_s]\le\epsilon,
 \qquad s\in\{0,1\}.\label{eq:ideal}
\end{equation}
The expectation is over independent complete runs under that law, matching
the seed-level estimand rather than treating packets as independent trials.
Unobserved packet ages, stochastic ingress and delayed immutable commands
make this a partially observed sequential problem. The proposed controller
does not solve \eqref{eq:ideal}. Instead, Algorithm 1 estimates a future queue,
the finite-grid ranking selects a command from that estimate, and Algorithm 2
screens a fixed policy parameter on separate calibration runs. The test screen
then evaluates its measured cost and miss fractions under each declared law.

This separation has two consequences. First, minimizing the one-step proxy
cost is not minimizing the full-run objective in \eqref{eq:cost}. A switching
penalty relative to the last requested expansion can differ from the actual
activation charge when commands reorder. Second, $\rho_s\le1$ is only a
decision surrogate. It cannot replace the constraint on $V_s$ in
\eqref{eq:ideal}. The model, algorithms and experiments consequently address
three different objects: a design target, an executable approximation, and
finite-sample evidence about that approximation.
'''

INTERPRET = r'''
\subsection{What the contrasts identify}
The strongest cost interpretation comes from P, R and J, not from pooling
all seven settings. Their qualified comparisons concern complete policies on
matched traces. P and R also belong to the two report-quality strata used in
calibration. Their fresh seeds test repeatability within those constructions,
not generalization to an unseen traffic family. J tests an unseen delay law,
but its announced delays are still available to the ledger at command issue.
Its result does not establish robustness to unannounced actuator latency.

The compute case C illustrates why cost and reliability must be interpreted
jointly. The proposed controller has no observed misses in either class,
yet the fixed reference fails its class-1 upper-endpoint screen. Therefore,
the result cannot be described as a qualified saving under the stated rule.
It is evidence about the two complete policies after relocating the
bottleneck, not an isolated estimate of the benefit of moving capacity.

M versus B is a controlled change in conditional batch dispersion on the
same traffic-state construction. Nevertheless, the realized queue and
reservation trajectories also change. A classwise miss difference need not
be monotone in arrival variance, because borrowing reallocates residual
service between classes. Neither aggregate plot identifies that scheduler
mechanism by itself. Per-slot packet-age and reservation traces would be
needed to distinguish it from forecast error.

In P, removing the ledger raises mean cost from 4159.85 to 4619.93 while
both policies have zero observed misses. The approximately 9.96\% reduction
relative to the no-ledger cost is therefore the cleanest diagnostic evidence
for the ledger at the selected headroom. It does not prove that queue
prediction is more accurate, because forecast errors were not recorded as
an outcome. The uncalibrated variant changes headroom rather than ledger
availability. Its cheaper outcome cannot establish an efficiency advantage
when the reliability screen fails. These two ablations identify different
design choices and should not be merged into a single causal claim.
'''

def algorithms(tex):
    return re.findall(r'\\begin\{minipage\}\{\.96\\linewidth\}.*?\\end\{minipage\}',tex,re.S)

def refine(tex):
    before=algorithms(tex)
    for label, replacement in [('architecture',ARCH),('timeline',TIME)]:
        pattern=r'\\begin\{figure\}\[htbp\]\\centering\s*\\begin\{tikzpicture\}.*?\\label\{fig:'+label+r'\}\s*\\end\{figure\}'
        # Restrict each search to its own figure, never consume an algorithm.
        figs=list(re.finditer(r'\\begin\{figure\}.*?\\end\{figure\}',tex,re.S))
        matches=[m for m in figs if r'\label{fig:'+label+'}' in m.group()]
        assert len(matches)==1
        m=matches[0]; tex=tex[:m.start()]+replacement+tex[m.end():]
    tex=tex.replace(r'\section{Calibrated Action-Aware Controller}',BRIDGE+r'\section{Calibrated Action-Aware Controller}')
    tex=tex.replace(r'\subsection{Connecting the curves to the model}',INTERPRET+r'\subsection{Connecting the curves to the model}')
    # Independent concluding section, without forcing a mostly empty page.
    tex=tex.replace('\\clearpage\n\\section{Conclusion}','\\section{Conclusion}')
    # Keep appendix headings with their tables and use end-matter space for
    # the actual reproducibility/availability contract, not filler text.
    repro=re.search(r'\\section\{Reproduction Contract\}.*?(?=\\section\*\{Data and Code Availability\})',tex,re.S)
    avail=re.search(r'\\section\*\{Data and Code Availability\}.*',tex,re.S)
    if repro and avail:
        endmatter=repro.group().replace(r'\section{Reproduction Contract}',r'\section*{Reproduction Contract}')+avail.group()
        tex=tex[:repro.start()]
        tex=tex.replace('\\clearpage\n\\appendix',endmatter+'\n\\clearpage\n\\appendix')
    assert algorithms(tex)==before and len(before)==2
    return tex
