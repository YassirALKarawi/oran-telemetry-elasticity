# Version 4: bounded capacity elasticity with cost and activation lag

## Scope and execution

```
python evaluate_v4.py --test
python evaluate_v4.py --seeds 20 --measure 3000 --output results_v4.json
```

Standard-library Python 3.10+. Four settings, four configurations, 20 new seeds
3000–3019 give 320 runs. Scenario definitions, 300-slot warmup, 3,000-slot
measurement cohort, 40-slot observation tail, arrival generation and synthetic
20-ms slots are unchanged. The parameters below were fixed before evaluation.
No admission rejection, packet dropping, deadline changes or favorable-seed
filtering is used. All measured unfinished overdue packets remain violations.

This is still an abstract tandem service model, not an NR or protocol-accurate
O-RAN simulator. Capacity means integer packet service units per slot, not
physical bandwidth or CPU cores. The extra capacity comes from an assumed
external provisionable pool and is explicitly bounded and charged; no
unlimited or free resources are introduced.

## Resource and cost model

Only transport and compute can expand. Radio capacity stays unchanged.
At each supervisory decision, choose integer additions e_transport and
e_compute in 0..M. Four configurations are evaluated:

| Configuration | Transport addition | Compute addition |
|---|---|---|
| fixed | Always zero | Always zero |
| always_on | Always 3 | Always 3 |
| elastic_cap1 | Dynamically 0..1 | Dynamically 0..1 |
| elastic_cap3 | Dynamically 0..3 | Dynamically 0..3 |

The always-on comparator starts pre-provisioned. Its capacity occupancy is
charged from slot zero but no initial switching fee is charged. For dynamic
policies, commands and their associated class shares take effect together
after ten slots (200 ms), never in the request slot. Commands have deterministic
equal delay and are applied in issue order, including deactivation. Activation
failures, stochastic provisioning delay and a shared multi-tenant pool are not
modeled yet. All configurations use the same control lag for share updates.

At slot t the service capacity is base_capacity_i(t)+active_extra_i(t).
The simulation engine knows true capacities but the controller's snapshots
report base capacity, queues and observed historical service. Known commands
are tracked by deterministic actuation. Report-based forecasts and the
uncertainty margin are evaluated at the intended activation time t+10.

Reported cost for a complete run is:

J = sum_t sum_i active_extra_i(t)
    + 0.25 sum_applied_commands sum_i |new_extra_i - old_extra_i|.

One extra service unit maintained for one slot costs one abstract cost unit.
There are no currency or real infrastructure price claims. Costs include
warmup and followup, and are not restricted to the measured arrival cohort.
Share-only changes have no switching cost in this pilot.

## Joint finite-grid decision

For each candidate pair of extra capacities and each common class share
alpha in {0.05,...,0.95}, evaluate the V3 two-class delay surrogate using
reported base capacity plus the candidate additions. Demand includes the
predicted queue, five slots of observed mean arrivals, an uncalibrated
dispersion margin and one representative service unit.

If a candidate meets both modeled delay targets, select the least-cost
candidate, then the smallest worst normalized delay. The decision-time cost
proxy is sum_i extra_i+0.25 sum_i |extra_i-previous_requested_extra_i|. This
single-step proxy is not an optimization of the entire run cost. Pending
commands can make previous requested capacity differ from current active
capacity. The real applied-command switching cost is accounted separately.

If no candidate meets both surrogate targets, select minimum worst normalized
delay and then cost, and expose infeasibility. The bounded grid has at most
16 capacity pairs times 19 shares = 304 candidate decisions. Exhaustive search
is exact on that small surrogate grid only. It is not a globally optimal
network resource allocation result or a chance-constraint guarantee.

All configurations use the same report-selection rule (the previous risk
heuristic), local work-conserving scheduler and report budget. Trace hashes,
request counts, delivery counts and generated arrivals match across each
seed/setting. Outcome-dependent report selections can differ. Reports have
the same padded-size assumption and do not consume transport resources.

## Measurements and inference

Classwise and arrivals-weighted deadline violations, resource occupancy cost,
switching units and modeled-feasibility fractions are retained per seed.
Paired bootstrap intervals use 2,000 resamples and are exploratory, without
multiplicity adjustment. Compare cost and quality jointly: extra resources
cannot be portrayed as a free algorithmic performance gain.

The always-on configuration is a reference, not an optimal performance upper
bound: its heuristic class allocation can be suboptimal even with more
capacity. No pure effect of telemetry selection is isolated in this experiment.
Radio may remain the bottleneck after transport/compute expansion.

## Verification

Seven new tests check resource bounds, zero expansion cost for fixed capacity,
always-on occupancy accounting, delayed activation, equal trace/report/arrival
budgets, explicit modeled infeasibility and deterministic reproducibility.
The earlier 17 tests remain applicable to their unchanged versions. All runs
also assert packet conservation and local service-capacity limits.

Run summarize_v4.py to generate RESULTS_V4.txt after results_v4.json exists.
No manuscript-readiness, real-world validity or journal acceptance is asserted.

## Recorded outcome

All 320 runs completed; 24 tests passed across the four preserved test suites.
All 17 prior package files were byte-checked as unchanged before packaging.

The expansion cap of 3 units per expandable stage improved both class sample
means relative to fixed capacity under all three stress settings:

| Setting | Fixed class 0 / class 1 | Elastic cap 3 class 0 / class 1 | Extra-resource cost saving versus permanent maximum |
|---|---|---|---|
| Transport congestion | 24.41% / 34.80% | 0 observed / 0 observed | 81.15% |
| Compute congestion | 23.35% / 34.18% | 0 observed / 0 observed | 80.80% |
| Higher report delay/loss | 21.95% / 35.09% | 0 observed / 0.12% | 79.98% |

The saving applies ONLY to incremental resource occupancy and switching cost
against the permanently provisioned maximum (3+3 units), not total network
cost, energy or a real financial budget. The full base infrastructure cost
is outside the model. More capacity is not free: the fixed comparator has
zero incremental cost but much worse stress performance.

No nominal misses occurred for any configuration. Nevertheless the dynamic
cap-3 method used mean incremental cost 176.04 versus zero for fixed capacity.
This reveals unnecessary nominal expansion caused by forecast conservatism.

Zero observed violations in a finite, correlated synthetic experiment must
not be interpreted as a zero violation probability or a guaranteed SLA.
With higher delay/loss, the dynamic method's class-1 mean is 0.118% versus
zero observed for permanently maximum capacity; its exploratory paired interval
for the difference is [0.000,0.322] percentage points. The dynamic policy does
not universally match permanently expanded capacity.

These results establish a capacity/quality/cost tradeoff in this abstraction,
not novelty or superiority over state-of-the-art orchestration. Before paper
claims, add optimized fixed-capacity baselines (not only permanent maximum),
resource-budget-matched policies, independently calibrated workloads and
service demands, telemetry cost on transport, control-latency sweeps, and
measurement-based validation. Retain nominal false-positive expansion and
adverse high-delay outcomes rather than removing inconvenient cases.
