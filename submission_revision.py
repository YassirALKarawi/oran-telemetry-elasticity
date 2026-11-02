"""Add an executed post-selection pending-command diagnostic."""
import json
from pathlib import Path

def revise_submission(t):
 d=json.loads((Path(__file__).parent/'pending_diagnostic.json').read_text())
 rows=[]
 for label,x in zip(['P','M','B','C','R','L','J'],d['summaries']):
  a=x['applied_only'];b=x['full'];lo,hi=x['full_minus_applied_ci']
  rows.append(f"{label} & {a['cost']:.1f} & {b['cost']-a['cost']:.1f} & [{lo:.1f}, {hi:.1f}] & {100*max(a['violation']):.3f} & {100*max(b['violation']):.3f}"+r'\\')
 block=r'''
An additional matched diagnostic separates applied-action history from pending-command information. The applied-only variant retains the complete applied ledger $\mathcal L$ but removes $\mathcal P$ from Algorithm~1, holding the currently active command throughout the future projection interval. Its projected state is therefore $\widehat q^{-}_{is}(t+L)=\operatorname{Project}_{is}(\mathcal R_t,\mathcal L,\varnothing,L)$. The full controller uses the same projection with $\mathcal P$, where $\varnothing$ denotes an empty pending-command list. Both variants use the locked headroom $\eta=0.75$, identical reports, command delays, action grids and seed-indexed exogenous traces. This post-selection diagnostic adds 140 executions on the original twenty seeds in each setting, without selecting new parameters or changing the original reliability screen. It is distinct from the no-ledger ablation, which removes applied-action replay as well.

Table~\ref{tab:pending} reports the applied-only cost and the paired difference $J_{\mathrm{full}}-J_{\mathrm{applied}}$. The violation columns report the larger of the two classwise seed-mean miss fractions. The intervals quantify seed-to-seed variation in the cost difference and do not certify reliability or adjust for multiple comparisons.
\begin{table*}[t]
\caption{Matched pending-command diagnostic. Cost differences are full minus applied-only, with paired 95\% intervals. Miss fractions are percentages.}
\label{tab:pending}
\centering\small
\begin{tabular}{lrrrrr}
\toprule
Setting & Applied-only cost & Cost difference & 95\% interval & Applied-only misses & Full misses\\
\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule
\end{tabular}
\end{table*}
'''
 x=d['summaries'][0];a=x['applied_only']['cost'];b=x['full']['cost'];diff=b-a
 block+=f'In P, retaining pending commands changes mean cost by {diff:.1f} units ({100*diff/a:.2f}\\% relative to applied-only). '
 block+=r'''All seven paired cost intervals include zero. Thus, these runs do not establish an incremental cost advantage from pending-command information alone. In L, the worst-class mean miss fraction increases from 6.804\% to 8.785\% with full replay, so pending-command awareness does not remove the long-delay failure. This isolates a narrower information effect than the original no-ledger comparison. Pending commands change the service used to extrapolate $\widehat q_{is}(t+L)$, which changes the normalized demand ratios $\rho_s$ and the selected integer expansion. The net effect depends on whether scheduled commands add or remove capacity before activation, and therefore need not improve cost and deadline misses simultaneously. The full and applied-only columns must be interpreted jointly rather than treating a lower $J$ alone as a better controller.
'''
 t=t.replace(r'\section{Discussion and Deployment Boundary}',block+'\n'+r'\section{Discussion and Deployment Boundary}')
 t=t.replace('all 1176 execution records,','all 1176 primary execution records and 140 additional diagnostic records,')
 t=t.replace('Additional diagnostic decompositions use these\nsaved executions without changing parameter selection or the\noriginal qualification rule.', 'Additional decompositions use the saved executions, while 140 matched diagnostic runs isolate pending-command information without changing parameter selection or the original qualification rule.')
 t=t.replace('Physical deployment and rare-event reliability validation remain future work.', 'A separate matched diagnostic finds no resolved incremental cost benefit from pending-command information alone, narrowing attribution of the observed ledger effect. Physical deployment and rare-event reliability validation remain future work.')
 return t
