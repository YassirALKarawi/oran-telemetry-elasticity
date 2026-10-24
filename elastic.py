"""Finite-grid capacity/share decision. Synthetic service units, not currency."""
import math
from experiment import forecast
from baseline.simulate import DEADLINES, allocate


def solve_elastic(reports, t, previous, maximum=3, delay=10, fixed=None,
                  use_prediction=True, use_margin=True):
    # Forecast at the intended activation time. This is an uncalibrated proxy.
    demand=[]
    for r in reports:
        age=t+delay-r['time']
        q=forecast(r,t+delay,True) if use_prediction else r['q']
        demand.append([q[s]+5*r['arrival'][s]+(math.sqrt(age*r['variance'][s]) if use_margin else 0)+1 for s in range(2)])
    extras = [(0,x,y) for x in range(maximum+1) for y in range(maximum+1)] if fixed is None else [fixed]
    best=None
    # Cache stage/share/extra contributions, avoiding repeated forecast work.
    cache={}
    for i in range(3):
        for extra in sorted({x[i] for x in extras}):
            for k in range(1,20):
                quota=allocate([k/20,1-k/20],max(0,int(reports[i]['capacity']))+extra)
                cache[i,extra,k]=[demand[i][s]/max(.001,quota[s])/DEADLINES[s] for s in range(2)]
    for extra in extras:
        cost=sum(extra)+.25*sum(abs(extra[i]-previous[i]) for i in range(3))
        for k in range(1,20):
            ratios=[sum(cache[i,extra[i],k][s] for i in range(3)) for s in range(2)]
            worst=max(ratios)
            # Feasible first, then cheapest. Infeasible: minimax then cost.
            score=(0,cost,worst,sum(ratios),k) if worst<=1 else (1,worst,cost,sum(ratios),k)
            if best is None or score<best[0]:
                best=(score,extra,k,ratios)
    _,extra,k,ratios=best
    return list(extra),[[k/20,1-k/20] for _ in range(3)],dict(
        model_feasible=max(ratios)<=1,predicted_ratios=ratios,
        maximum_normalized_slack=max(0,max(ratios)-1),alpha=k/20)
