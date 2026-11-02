# Joint transport routing and processing allocation

An executable, simulation-only foundation for the thesis **Optimal Resource Allocation in ORAN with SDN-Managed Orchestration**. This is not a new validated O-RAN algorithm or a submission-ready manuscript. No laboratory or RIC deployment is required for this Python model.

## Model

Each offered request specifies bandwidth, processing demand and an end-to-end delay budget. A decision selects one unsplittable route and one processing destination, or rejects the request. Shared link and processing capacities cannot be exceeded. Delay is the sum of fixed link delays and a fixed destination processing delay. It does not include stochastic queueing or radio propagation/channel modeling. Costs are abstract reserved-resource costs, not measured energy.

The exact mixed-integer model maximizes the number of admitted requests, then minimizes cost. The fast heuristic considers complete route/destination alternatives using the same constraints. A placement-first diagnostic chooses the cheapest processing node before checking transport. It is a deliberately simple comparator, not a state-of-the-art external baseline.

## Reproduce

Use Python 3.10 or newer on an ordinary computer:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r joint_allocation/requirements.txt
python -m unittest discover -s joint_allocation -p 'test_*.py' -v
python joint_allocation/experiment.py
```

On Windows activate the virtual environment using `.venv\Scripts\activate` instead. The full executed data are in `results.json.gz`, readable with Python's standard gzip and json modules.

## Executed validation

Three tests passed, including twenty independent exhaustive comparisons against the exact solver, zero link capacity, and impossible delay budgets. One hundred development instances were evaluated with three methods, giving 300 algorithm executions. All output assignments are checked for bandwidth, processing and delay feasibility.

| Method | Mean served out of 12 offered | Cases matching the optimal service count |
|---|---:|---:|
| Exact reference | 8.55 | 100/100 |
| Joint greedy | 8.06 | 56/100 |
| Placement-first diagnostic | 4.30 | 0/100 |

At matching admission counts, the greedy method still averages 8.73 extra abstract cost units above the optimum. Equal counts do not ensure the same requests are selected. The weak placement-first diagnostic is not sufficient evidence of research novelty or competitive superiority. No percent cost reduction is claimed across unequal service levels. Seeds, inputs, assignments, resource loads, costs and machine-dependent timings are preserved in the result artifact.

## Research path

1. **First paper candidate:** coupled routing/processing allocation. Add a technically distinct algorithm and credible external baselines, then evaluate scaling and service/cost tradeoffs on independent topologies. The existing exact reference and greedy methods are comparison infrastructure.
2. **Second paper candidate:** uncertain traffic and stale observations, only after validating the first model. Require separate robust comparators and independent evidence.
3. **Third paper candidate:** recovery under link or processing-node failure. Require explicit failure/repair modeling and comparisons with established protection schemes.

These are research targets, not three completed contributions. The original thesis title is retained. Sharing code and a platform across papers must be disclosed, and each manuscript needs its own scientific question and experiments.
