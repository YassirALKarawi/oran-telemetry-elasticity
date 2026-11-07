"""Descriptive paired results on fixed test traces."""
import json
from pathlib import Path
from statistics import mean

here=Path(__file__).resolve().parent
d=json.loads((here/"results.json").read_text())
rows=d["traces"]
assert len({r["trace_seed"] for r in rows})==15
print("| Scenario | Controller | Cost | Extra unit-slots | Mean per-trace p99 (slots) | Misses / mature packets |")
print("|---|---|---:|---:|---:|---:|")
for scenario in dict.fromkeys(r["scenario"] for r in rows):
    for label,keys in [("Thesis",["thesis"]),("Greedy",["greedy"]),("Adapted DDQN",list(d["selection"]))]:
        data=[r["results"][k] for r in rows if r["scenario"]==scenario for k in keys]
        for v in data:
            assert v["offered"]==v["delivered"]+v["outstanding"]+v["lost"]
            assert all(a<=b for a,b in zip(v["stage_service"],v["stage_supply"]))
        cols=[mean(v[k] for v in data) for k in ["total_cost","extra_unit_slots","delivered_p99_slots"]]
        failures=sum(v["deadline_misses"] for v in data)
        denom=sum(v["mature_packets"] for v in data)
        print(f"| {scenario} | {label} | {cols[0]:.2f} | {cols[1]:.1f} | {cols[2]:.2f} | {failures} / {denom} |")
