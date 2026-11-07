"""Summarize recorded paired tests; fixed controllers contribute once per trace."""
import json
from pathlib import Path
from statistics import mean

here = Path(__file__).resolve().parent
spec = json.loads((here/"protocol.json").read_text())
parent = json.loads((here.parent/"protocol.json").read_text())
seeds = parent["training_seeds"]
budgets = spec["budget_episodes"]
summary = {}
lines = [
    "# Sensitivity to the training budget in the tandem simulator", "",
    "The protocol was frozen before the new tests at commit 3de8655e54ee8a357f8edc7777f0b54a5388c699. Each seed followed one training trajectory. All budgets kept the same model, reward, exploration schedule, environment and action set. Longer training also exposed the controller to more training traces from the same scenario generator. Each budget had two validation candidates and used the same three validation traces. The five selected short-budget models matched the previously archived weights tensor for tensor.",
    "", "## Held-out results", "",
    "Costs, resource use, and per-trace p99 delays are arithmetic means. Lower cost is preferable under the prespecified backlog, capacity and switching penalty. Misses and mature-packet denominators are pooled across each row; the learned policies repeat the same arrivals under five independently seeded models.",
    "", "| Scenario | Controller / training decisions | Cost | Extra unit-slots | Mean p99 (slots) | Misses / eligible |",
    "|---|---|---:|---:|---:|---:|"
]
for scenario, ids in spec["test_seeds"].items():
    rows = json.loads((here/(scenario+".json")).read_text())
    assert [r["seed"] for r in rows] == ids
    summary[scenario] = {}
    for policy in ["thesis","greedy",*budgets]:
        learned = isinstance(policy,int)
        keys = [f"{policy}/{s}" for s in seeds] if learned else [policy]
        data = [r["outcomes"][k] for r in rows for k in keys]
        cost = mean(v["total_cost"] for v in data)
        misses = sum(v["deadline_misses"] for v in data)
        denom = sum(v["mature_packets"] for v in data)
        label = f"Adapted DDQN / {policy*72:,}" if learned else policy.title()
        extra = mean(v["extra_unit_slots"] for v in data)
        delay = mean(v["delivered_p99_slots"] for v in data)
        lines.append(f"| {scenario} | {label} | {cost:.2f} | {extra:.1f} | {delay:.2f} | {misses} / {denom} |")
        record = dict(mean_cost=cost, mean_extra=extra, mean_p99=delay, misses=misses, eligible=denom)
        if learned:
            deltas = [mean(r["outcomes"][k]["total_cost"]-r["outcomes"][f"{budgets[0]}/{s}"]["total_cost"]
                           for r in rows) for k,s in zip(keys,seeds)]
            record.update(paired_cost_differences=deltas, mean_difference=mean(deltas),
                          seeds_improving=sum(v<0 for v in deltas))
        summary[scenario][str(policy)] = record
lines.extend(["", "## Paired cost differences relative to 1,296 decisions", "",
              "| Scenario | Budget | Mean difference | Seed-level means below short budget |",
              "|---|---:|---:|---:|"])
for sc, group in summary.items():
    for budget in budgets[1:]:
        r = group[str(budget)]
        lines.append(f"| {sc} | {budget*72:,} | {r['mean_difference']:+.2f} | {r['seeds_improving']} / 5 |")
lines.extend(["", "## Interpretation and reproducibility", "",
    "There are five training seeds and five new traffic traces per scenario. Models at different budgets on the same training seed are paired. Aggregate comparisons are descriptive. The published native PRORL transfer-task benchmark uses a different action space and reward. These tests measure a PRORL-derived Double DQN controller in a synthetic tandem queue. End-to-end SDN/RIC actuation remains to be verified.",
    "", "The three scenario JSON files contain every test result and trace digest. Each seed file contains validation costs for all candidate episodes and the three selected model states with SHA-256 digests. From the repository root use the pinned baseline_prorl interpreter to run common_environment/adapted/budget_study/study.py with replay to verify all 255 policy–trace outcomes. The train and test phases regenerate the weights and results, respectively. Run summarize.py to rebuild these tables.", ""])
(here/"README.md").write_text("\n".join(lines))
(here/"summary.json").write_text(json.dumps(summary,indent=2,allow_nan=False)+"\n")
