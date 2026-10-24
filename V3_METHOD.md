# Version 3: two-class modeled deadline constraints

## Implementation and run command

```
python evaluate_v3.py --test
python evaluate_v3.py --seeds 20 --measure 3000 --output results_v3.json
```

The original experiment.py and all earlier raw results remain unchanged.
engine_v3.py adds an allocator hook while retaining the same simulation event
order. A numeric regression test checks equivalence for the previous policy.
constraints.py implements the finite search; evaluate_v3.py performs the new
evaluation. Python 3.10+, no additional packages.

## Mathematical surrogate, not an actual delay bound

For stage i, class s and delivered-report timestamp tau_i, the prediction is

qhat_i,s(t) = max(0, q_i,s(tau_i) + (t-tau_i)(lambda_i,s-mu_i,s)).

lambda and mu are means of locally observed arrivals and departures over the
20-slot report history. They are not offered-load or capacity guarantees.
The uncertainty proxy is u_i,s(t) = sqrt((t-tau_i) variance_i,s), where the
variance is that of historical per-slot arrivals minus departures. This proxy
has not been calibrated against prediction residuals and is not a statistical
confidence bound. In particular the IID scaling can fail under temporal
correlation, changed allocation or traffic shifts.

For a common class-0 share alpha in {0.05,0.10,...,0.95}, integer stage quotas
n_i,s(alpha) follow the original largest-remainder allocator using the stage's
last reported capacity. Define the predicted normalized delay surrogate

r_s(alpha) = sum_i [(qhat_i,s + 5 lambda_i,s + u_i,s + 1)
                    / max(0.001,n_i,s(alpha))] / D_s.

The factor 5 is the existing supervisory control interval, not a fitted
parameter. One unit represents the tagged packet's service demand. The 0.001
denominator floor is a finite numerical penalty for a zero quota, not physical
service capacity. Actual local service is always limited by the true stage
capacity. The surrogate ignores complex tandem arrival correlations and
packet age distributions and therefore must not be called a rigorous delay
or violation-probability bound.

Solve min_alpha max_s r_s(alpha) by enumerating all 19 shares. Ties use the sum
of ratios, distance to equal share and then alpha. Equivalently introduce z and
minimize z subject to r_0(alpha)<=z and r_1(alpha)<=z on this finite grid. This
is a minimax relaxation of the two target constraints r_s<=1, not a proof of
an optimal network-wide allocation.

If the best z<=1, the selected share is modeled-feasible. If z>1, neither target
is silently relaxed: record modeled infeasibility and maximum normalized slack
z-1, then apply the minimax-slack choice. There is no hidden packet rejection,
admission control, extra capacity, deadline change or class dropping.

The local scheduler still lends unused reserved capacity with an earliest
absolute-deadline rule. Local execution uses its own current queues; the
supervisory search sees only delivered reports. All configurations make the
same number of report requests at the same cadence, with the same request-loss
sequence and padded fixed-size report assumption. Telemetry does not consume
transport capacity in this pilot.

## Evaluation frozen before results

Twenty new seeds 2000–2019, distinct from both prior experiments. Four existing
settings and six configurations yield 480 runs. A 300-slot warmup, 3,000-slot
arrival cohort, 40-slot followup and synthetic 20-ms slots are unchanged.
Six variants: modern_oldest, modern_risk, constrained_periodic,
constrained_oldest, constrained_risk and constrained_no_margin.

The four constrained variants isolate report-selection and uncertainty-margin
effects. No-margin uses the same report selection as constrained_risk. All
methods are tested on both service classes; an arrivals-weighted total rate
is also reported, without treating it as a substitute for the classwise rates.
Two thousand paired seed-bootstrap resamples produce exploratory intervals.
No multiplicity adjustment or confirmatory hypothesis test is applied.

Modeled-feasibility fractions include all decision epochs, including warmup
and followup, and must not be equated with measured-cohort SLA satisfaction.
The actual packet deadline violation metrics resolve the full measured cohort
at the terminal horizon, including unfinished overdue packets.

## Tests and limits

Six new checks cover optimality on the enumerated surrogate grid, explicit
modeled infeasibility, nonnegative margin effect at fixed alpha, responsiveness
to class-1 workload, numeric equivalence of unchanged v2 policy behavior, and
common event/report budgets plus deterministic reproducibility.

Six original and five v2 tests also remain in the package. The allocator is
constraint-aware only with respect to its surrogate. Actual two-class QoS
constraints and chance constraints remain unproven. This is an engineering
experiment, not a completed publication-grade simulation or manuscript.

## Recorded outcome and capacity audit

480 new runs completed and all 17 tests passed (6 original, 5 v2, 6 v3).
All eight original files of the v2 package were verified byte-identical before
packaging the extension. New seeds were not used to tune the method afterward.

Against modern_oldest on the same new seeds, constrained_risk changes the
deadline violation sample means as follows:

| Setting | Class 0, old to new | Class 1, old to new | Arrivals-weighted, old to new |
|---|---:|---:|---:|
| Transport stress | 38.88% to 23.91% | 33.21% to 35.43% | 34.95% to 31.88% |
| Compute stress | 37.37% to 22.95% | 32.71% to 34.82% | 34.14% to 31.17% |
| Higher delay/loss | 39.23% to 22.22% | 32.29% to 35.68% | 34.42% to 31.54% |

No nominal deadline misses were observed for either class or either policy in
this finite experiment. This is not evidence of zero true violation probability.
The class-1 paired-bootstrap intervals versus modern_oldest are positive for
all stress settings. Thus joint non-degradation is not achieved. The allocation
is more favorable for class 0 and the weighted average, but it does not protect
both classes under congestion.

An independent necessary capacity check (feasibility_audit.py) counts packets
released in a burst interval [a,b). Every one of them must receive one unit of
bottleneck service no later than b+max(D_s) for all deadlines to be met. The
capacity available in [a,b+max(D_s)) is an optimistic upper limit, since it
ignores competing earlier/later packets and all other pipeline constraints.
If arrival count exceeds even this upper limit, some burst packets must miss
their deadlines under every scheduler in this model.

This necessary condition failed in 200 out of 200 fully observed measured
burst windows across the two bottleneck scenarios and 20 seeds. The extra
report-delay/loss case reuses the transport capacity pattern and is not counted
again. See feasibility_audit.json for per-window counts and lower bounds.

Conclusion: a no-miss guarantee for both classes is impossible for these
particular burst windows with the current fixed capacity and no rejection.
This says nothing about a positive miss-rate target being impossible. Neither
the negative result nor the surrogate solver establishes a probabilistic SLA.

The next useful model must explicitly study resource elasticity, alternative
processing/routing, or transparent admission control. Rejected work must be
reported separately and cannot be hidden to manufacture an SLA improvement.
Simply changing telemetry priorities cannot remove a verified service deficit.
