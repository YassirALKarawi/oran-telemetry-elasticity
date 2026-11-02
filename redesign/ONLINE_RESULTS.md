# Executed causal-controller comparison

The causal controller is implemented in `online.py`. It sees only released packets, committed resource leases, and contractual base service floors. It never reads future arrivals or realized future capacity. `ONLINE_MODEL.md` states its conditional guarantee and proof.

Eight tests pass, including independent exhaustive checks for the reference and 50 randomized execution checks for the causal controller. The causal experiment contains 240 runs plus 80 offline optimization bounds. A subsequent exploratory static frontier adds 180 runs across nine capacity configurations. These are synthetic development experiments, not real-network validation or independent confirmation of a new contribution.

| Actuation delay | Timely / offered | Rejected / offered | Mean added unit-slots | Offline attainable admissions / offered |
|---:|---:|---:|---:|---:|
| 1 | 82.92% | 17.08% | 42.65 | 99.58% |
| 3 | 90.14% | 9.86% | 41.00 | 99.58% |
| 6 | 60.97% | 39.03% | 6.25 | 99.58% |
| 12 | 56.11% | 43.89% | 0.00 | 85.42% |

All accepted packets meet their deadlines under the assumed service floors. This does not mean that all offered traffic is served. The rejected fractions above are essential to interpretation.

The complete static frontier finds that one extra unit at each downstream stage attains 92.92% timely delivery at cost 48, the same service level as the previously considered cost-96 maximum-capacity benchmark. At delay 3, the causal policy attains 90.14% at cost 41. It therefore does not establish superiority at matched reliability: its lower cost accompanies 2.78 percentage points less timely offered traffic. The delay-1 policy is worse than delay-3 in both mean cost and timely fraction, exposing sensitivity of greedy lease timing. No cases were removed.

A deterministic contractual floor has not been established from the inspected radio records. The mechanism is executable and its conditional invariant is tested, but its empirical guarantee, external comparative advantage, and publishable novelty remain unresolved. The existing manuscript must not be relabeled as a validated version of this redesign.

## Reproduce

```bash
python -m unittest discover -s redesign -p 'test_*.py' -v
python redesign/online_benchmark.py
python redesign/static_frontier.py
```

All per-run reservations, leases, rejections and outcomes are distributed in the two gzip JSON result files.
