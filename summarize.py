"""Generate a plain-text audit summary from actual experiment output."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent
data = json.loads((root / "results_v2.json").read_text())
lines = ["SYNTHETIC PILOT V2: EXPLORATORY RESULTS", "",
         f"Runs: {len(data['runs'])}; seeds per setting/configuration: {data['seeds']}",
         "Units: violation rates in percent; backlog in packets.",
         "Not a validated O-RAN implementation or a publication-ready result.", ""]
for row in data["summaries"]:
    lines.append(f"{row['case']:42} {row['config']:18} "
                 f"class0={100*row['mean_violations'][0]:7.3f}% "
                 f"class1={100*row['mean_violations'][1]:7.3f}% "
                 f"backlog={row['mean_backlog']:.3f}")
lines += ["", "Paired modern_risk minus comparator: class0 percentage points",
          "Exploratory 95% paired-bootstrap intervals; no multiplicity correction."]
for row in data["paired_comparisons"]:
    low, high = row["paired_bootstrap_ci95"]
    lines.append(f"{row['case']:42} {row['comparison']:36} "
                 f"difference={100*row['mean_difference']:.3f} "
                 f"CI=[{100*low:.3f}, {100*high:.3f}]")
text = "\n".join(lines) + "\n"
(root / "RESULTS.txt").write_text(text, encoding="utf-8")
print(text)
