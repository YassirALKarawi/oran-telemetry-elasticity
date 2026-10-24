# Telemetry-aware capacity elasticity in a two-class tandem service chain

## Scope and relation to the thesis

Approved thesis: **Optimal Resource Allocation in ORAN with SDN-Managed Orchestration**.
Student: Fatima Subhi Khaleel, fatima.subhi_eng@uodiyala.edu.iq.

The implemented study is a synthetic three-stage queueing model motivated by
radio, transport and computation. Those names do not instantiate a 3GPP radio,
an SDN controller, or an O-RAN functional split. A packet consumes one service
unit at each stage. No packet size, CPU-cycle demand or resource-block mapping
has been calibrated. The 20 ms slot is a synthetic time conversion, not an NR
transmission-time interval. Class deadlines are 300 and 800 ms, not URLLC targets.

## Symbols

| Symbol | Meaning and units |
|---|---|
| t, T | Slot index and total simulated slots |
| i in {1,2,3} | Abstract service stage |
| s in {0,1} | Traffic class |
| A_s(t) | New class-s packets arriving at stage 1 in slot t |
| Q_is(t) | Class-s queue at stage i at start of slot, before external arrivals |
| S_is(t) | Packets served at stage i during slot t |
| c_i(t) | Exogenous base service capacity, packets per slot |
| e_i(t) | Active extra capacity, packets per slot |
| x_i | Requested extra capacity, with x_1=0 and x_2,x_3 in {0,1,2,3} |
| alpha | Class-0 weight, in {0.05,0.10,...,0.95} |
| D_s | Deadline in slots, D_0=15 and D_1=40 |
| b_p, f_p | Packet birth and completion slots |
| tau_i | Timestamp of latest received stage-i report |
| a_i | Age t-tau_i of the controller's report |
| lambda_is, mu_is | Reported historical mean arrivals and service, packets per slot |
| v_is | Reported population variance of net arrivals minus service |
| L | Command activation delay in slots, default 10 |
| h | Control/report-request interval, 5 slots |
| W | Local report history, at most 20 preceding slots |
| rho_s | Normalized surrogate delay score, not a guaranteed delay ratio |
| eta | Switching-price coefficient, 0.25 abstract units per changed capacity unit |

## Queue evolution and local scheduling

At stage 1 the available queue is Q_1s(t)+A_s(t). At stages 2 and 3 it is Q_is(t).
The implementation serves downstream stages first, so packets cannot receive
service at two stages in the same slot. Consequently:

Q_1s(t+1) = Q_1s(t) + A_s(t) - S_1s(t)

Q_is(t+1) = Q_is(t) - S_is(t) + S_(i-1)s(t), i=2,3.

At each stage, the active capacity C_i(t)=c_i(t)+e_i(t) is split using largest
remainders with weights (alpha,1-alpha). Each class first receives up to its
quota. Unused units are reassigned to the next available packet with earliest
absolute deadline b_p+D_s. Equal deadlines favor class 0. FIFO is retained within
each class. This is quota-first scheduling with deadline-based borrowing, not a
claim of globally optimal earliest-deadline-first scheduling.

**Conservation proposition.** At every slot, cumulative generated packets equal
cumulative completed packets plus all queued packets. Proof: summing the queue
equations over stages cancels every intermediate departure/arrival pair.

**Work-conservation proposition.** Total stage service equals the smaller of
active capacity and the eligible queue length. Proof: initial quotas cannot
overserve either class. Every remaining unit is allocated while an eligible
packet exists. Termination occurs only when capacity or all eligible queues are
exhausted. This does not imply deadline feasibility.

**Minimum latency proposition.** Every completed packet has f_p-b_p+1 >= 3.
Proof: each packet traverses three stages and cannot traverse two in one slot.

## Telemetry and information boundaries

Exactly one report is requested every h=5 slots. Request-index loss flags are
generated independently of data traffic and reused across policies. Lost
reports are not retransmitted. A delivered report contains queue lengths,
base capacity, and the last W local arrival/service samples summarized by
means and variance. It is sampled after external arrivals but before service.
Only delivered reports are available to the remote controller. The local
scheduler sees its own queue and actual active capacity.

Age is computed from the measurement timestamp, not the reception timestamp.
At controller time t, the default extrapolation at activation time t+L is:

qhat_is = max(0, q_is(tau_i)+(t+L-tau_i)(lambda_is-mu_is)).

Reported service depends on earlier active expansion, whereas the reported
capacity is base capacity. This mismatch is intentional in the current
heuristic and is a model risk, especially when multiple commands are pending.
The predictor does not simulate the pending-command pipeline.

The full telemetry policy scores stage i using

P_i = sum_s sqrt((t-tau_i)*v_is+1)/D_s * (1+qhat_is(t)/max(1,c_i_reported))
      + 0.01*(t-tau_i).

The largest score is refreshed, with ties favoring lower stage index. The linear
age term is a preference, not a formal no-starvation guarantee. Round-robin and
oldest-first variants use the same request count, delays and loss flags.

## Finite-grid decision problem

For candidate expansion x and common class share alpha, let r_is(x,alpha) be
the largest-remainder quota formed from reported base capacity plus x_i.
Define the activation-time demand surrogate

z_is = qhat_is + h*lambda_is + sqrt((t+L-tau_i)*v_is) + 1

and rho_s(x,alpha) = sum_i z_is / max(0.001,r_is(x,alpha)) / D_s.

The floor 0.001 is a numerical penalty when a quota is zero. It is not real
fractional packet service. The square-root term resembles accumulation of
independent net-flow noise, but that independence is not established in this
coupled queueing system. Therefore it is neither a confidence bound nor a
chance constraint. A candidate is called **surrogate feasible** only when
max_s rho_s <= 1.

Let g(x)=sum_i x_i+eta*sum_i abs(x_i-x_i_previous_requested). The algorithm uses
the following lexicographic ranking, with k=20*alpha:

- Surrogate feasible: (0, g, max rho, sum rho, k).
- Surrogate infeasible: (1, max rho, g, sum rho, k).

Expansion pairs are enumerated in ascending order and exact ties keep the
first candidate. There are 16*19=304 candidates for the dynamic controller and
19 for a fixed expansion. Output capacity and shares are enqueued together for
activation at t+L. Commands are not cancelled or coalesced. The static comparator
starts preprovisioned, while its share commands have the same L.

**Finite-grid optimality proposition.** The returned candidate minimizes the
stated lexicographic score over the enumerated grid. Proof: the running incumbent
is the best element among all candidates already visited. Induction over the
finite enumeration leaves the best element of the full grid. This result does
not establish continuous, stochastic, long-horizon or physical-system optimality.

**Complexity.** With I stages, S classes, K shares, and M expansion combinations,
the direct search costs O(M*K*I*S). Here I=3, S=2, K=19, M=16. Cached stage
contributions reduce repeated arithmetic but do not improve the exponential
growth M=(Emax+1)^(I-1) if many expandable stages are introduced. Report-history
updates cost O(I*S*W). Packet simulation cost also depends on traffic and backlog.

## Actual objective and measured cohort

Reported incremental cost is

J = sum_(t=0)^(T-1) sum_i e_i(t)
    + eta*sum_(applied changes t) sum_i abs(e_i(t)-e_i(t-1)).

Preprovisioned initial static capacity has no switching fee. Its capacity-time
cost is still included. The objective excludes base-network cost, energy and
money. The per-decision score g is not the full-horizon objective J.

Packets born in slots 300 through 3299 are the measured cohort. Simulation
continues with background arrivals through slot 3339. A packet violates its
deadline if f_p-b_p+1>D_s. Any measured packet still queued at the end is also a
confirmed violation because its deadline has passed. The class rate is misses
divided by all measured arrivals of that class, not completed packets alone.
The completed-only delay percentile is secondary and can be survivor-biased.

## Necessary capacity cut, not a sufficient schedulability condition

Consider packets released in integer slots [a,b), all traversing stage i, with
maximum relative deadline Dmax. Every on-time packet must receive its stage-i
service within [a,b+Dmax-1). Therefore the looser capacity interval [a,b+Dmax)
also gives a necessary condition:

sum_(t=a)^(b-1) sum_s A_s(t) <= sum_(t=a)^(b+Dmax-1) C_i(t).

If demand exceeds even the capacity of this enlarged interval, at least the
difference cannot meet all deadlines. This proves impossibility of zero misses
for that interval and capacity trace, not impossibility of a positive miss-rate
target. Passing the inequality does not prove schedulability because ordering,
class deadlines and the other stages still matter.

## Defensible claim boundary

This formulation supports reproducible experiments on delayed information and
bounded capacity elasticity. It does not establish O-RAN interface compliance,
SDN path optimization, real CPU autoscaling times, URLLC reliability, or a novel
state-of-the-art result. Those require separate modeling and validation evidence.
