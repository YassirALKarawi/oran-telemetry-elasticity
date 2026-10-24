"""Joint two-class allocation over a fixed grid of common class shares.

Constraints are delay SURROGATES evaluated on delivered reports. They are not
chance constraints, calibrated bounds, or a guarantee on actual packet delay.
"""
import math
from experiment import forecast
from baseline.simulate import DEADLINES, allocate


def evaluate(reports, t, alpha, uncertainty=True):
    delays = [0.0, 0.0]
    for report in reports:
        q = forecast(report, t, True)
        age = t - report["time"]
        cap = max(0, int(report["capacity"]))
        quota = allocate([alpha, 1-alpha], cap)
        for s in range(2):
            margin = math.sqrt(age * report["variance"][s]) if uncertainty else 0.0
            # Queue workload and one abstract service unit for a representative
            # packet. Include predicted arrivals over one control interval.
            demand = q[s] + 5 * report["arrival"][s] + margin + 1
            delays[s] += demand / max(.001, quota[s])
    return [delays[s] / DEADLINES[s] for s in range(2)]


def solve(reports, t, uncertainty=True):
    """Exact exhaustive search on this 19-candidate grid, not a global solver.

Minimize the worst normalized predicted delay. Feasible means both modeled
delay ratios <= 1. Under modeled infeasibility keep the minimax-slack choice
and expose the infeasibility; never silently change a target or discard work.
"""
    best = None
    for k in range(1, 20):
        alpha = k / 20
        ratios = evaluate(reports, t, alpha, uncertainty)
        score = (max(ratios), sum(ratios), abs(alpha-.5), alpha)
        if best is None or score < best[0]:
            best = (score, alpha, ratios)
    _, alpha, ratios = best
    return [[alpha, 1-alpha] for _ in range(3)], dict(
        model_feasible=max(ratios) <= 1, predicted_ratios=ratios,
        maximum_normalized_slack=max(0, max(ratios)-1), alpha=alpha)
