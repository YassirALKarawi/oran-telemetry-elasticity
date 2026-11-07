"""Verify the five PRORL training runs and aggregate paired frozen-policy evaluations."""
import argparse
from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
from statistics import mean, stdev

import torch

RUN = Path(__file__).resolve().parent
PROTOCOL = json.loads((RUN / "FIVE_SEED_PROTOCOL.json").read_text())
AGENTS = ("prorl", "greedy", "heuristic")


def read(name):
    return json.loads((RUN / name).read_text())


def write(name, value):
    (RUN / name).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def digest(name):
    return hashlib.sha256((RUN / name).read_bytes()).hexdigest()


def leaves(value):
    if isinstance(value, dict):
        for child in value.values():
            yield from leaves(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            yield from leaves(child)
    else:
        yield value


def check_numbers(data):
    count = 0
    for value in leaves(data):
        if type(value) in (float, int):
            assert math.isfinite(value)
            count += 1
    assert count
    return count


def verify_training(seed):
    prefix = "recovered_full" if seed == 10 else f"seed{seed}_full"
    data = read(prefix + ".json")
    config = data["config"]
    assert config["random_seeds"] == dict(training=seed, validation=[100], evaluation=[1000, 1100, 1200])
    bootstrap = config["environment"]["agent"]["double_dqn"]["bootstrap_steps"]
    decisions = len(data["training/action_history/is_random"])
    assert bootstrap == 3000 and config["run"]["training_iterations"] == 86400
    assert decisions == 89400 and data["training/total_steps"] == decisions - 1
    validation = config["run"]["validation_run"]
    assert validation["enabled"] and validation["validation_keep_metric"] == "validation/avg/reward/utility"
    scores = data[validation["validation_keep_metric"]]
    assert scores
    initial = []
    for eid in PROTOCOL["initial_evaluation_seeds"]:
        assert data[f"evaluation-{eid}/episode/length"] == [168]
        assert len(data[f"evaluation-{eid}/action_history/add"]) == 168
        initial.append(data[f"evaluation-{eid}/reward/utility/total"][0])
    utility = data["evaluation/avg/reward/utility"][-1]
    assert math.isclose(mean(initial), utility, abs_tol=0.00003)
    weights = torch.load(RUN / (prefix + ".pt"), map_location="cpu", weights_only=False)
    tensors = [item for item in leaves(weights) if torch.is_tensor(item)]
    assert tensors and all(torch.isfinite(t).all().item() for t in tensors)
    artifacts = [prefix + ".json", prefix + ".pt"]
    if (RUN / (prefix + ".log")).is_file():
        artifacts.append(prefix + ".log")
    audit = dict(seed=seed, decisions=decisions, bootstrap=bootstrap,
                 initial_evaluation_seeds=PROTOCOL["initial_evaluation_seeds"], steps_per_evaluation=168,
                 initial_episode_utilities=initial, utility=utility,
                 best_validation_iteration=scores.index(max(scores)), best_validation_utility=max(scores),
                 counts=dict(numbers=check_numbers(data), tensors=len(tensors)),
                 all_numeric_results_finite=True, all_model_tensors_finite=True,
                 source=PROTOCOL["source"], diff_sha256=PROTOCOL["diff_sha256"],
                 sha256={name: digest(name) for name in artifacts})
    return audit, config


def directory(seed, demand):
    if demand == 80:
        return f"holdout_seed{seed}"
    prefix = "" if seed == 10 else f"seed{seed}_"
    return f"{prefix}demand_shift_{demand}"


def verify_extended(seed, demand, audit, config):
    folder = directory(seed, demand)
    protocol = read(f"{folder}/protocol.json")
    eids = PROTOCOL["extended_evaluation_seeds"]
    assert protocol["training_seed"] == seed and protocol["new_training"] is False
    assert protocol["evaluation_seeds"] == eids
    model = next(name for name in audit["sha256"] if name.endswith(".pt"))
    assert protocol["source_model_sha256"] == audit["sha256"][model]
    summary = read(f"{folder}/summary.json")
    values = {}
    for agent in AGENTS:
        data = read(f"{folder}/{agent}.json")
        check_numbers(data)
        c = data["config"]
        assert c["random_seeds"] == dict(training=seed, validation=[100], evaluation=eids)
        assert c["run"]["run_mode"] == "evaluation"
        assert c["environment"]["agent"]["type"] == agent
        assert {k:v for k,v in c["environment"].items() if k != "agent"} == {
            k:v for k,v in config["environment"].items() if k != "agent"}
        expected = deepcopy(config["emulator"])
        expected["model"]["synthetic_model"]["demand_absolute_value"] = demand
        assert c["emulator"] == expected
        episodes = []
        for eid in eids:
            assert data[f"evaluation-{eid}/episode/length"] == [168]
            assert len(data[f"evaluation-{eid}/times/choose_action"]) == 168
            [score] = data[f"evaluation-{eid}/reward/utility/total"]
            episodes.append(score)
        average = data["evaluation/avg/reward/utility"][-1]
        assert math.isclose(mean(episodes), average, abs_tol=0.00003)
        assert average == summary[agent]["reward/utility"]
        values[agent] = dict(average=average, episodes=episodes)
    return values


def compare():
    runs = {}
    reference_config = None
    results = {load: {} for load in PROTOCOL["demand_shifts"]}
    for seed in PROTOCOL["training_seeds"]:
        audit, config = verify_training(seed)
        normalized = deepcopy(config)
        normalized["random_seeds"]["training"] = 10
        if reference_config is None:
            reference_config = normalized
        assert normalized == reference_config
        runs[seed] = audit
        for demand, group in results.items():
            group[seed] = verify_extended(seed, demand, audit, config)
    aggregates = {}
    for demand, group in results.items():
        scores = [entry["prorl"]["average"] for entry in group.values()]
        reference = {}
        for agent in ("greedy", "heuristic"):
            ref = group[10][agent]
            assert all(entry[agent] == ref for entry in group.values())
            val = ref["average"]
            reference[agent] = dict(utility=val, mean_difference=mean(scores)-val,
                                    training_seeds_above=sum(score > val for score in scores))
        aggregates[demand] = dict(mean=mean(scores), sample_sd=stdev(scores), minimum=min(scores),
                                  maximum=max(scores), baselines=reference)
    write("FIVE_SEED_RESULTS.json", dict(training=runs, evaluation=results, aggregate=aggregates,
                                         protocol_sha256=digest("FIVE_SEED_PROTOCOL.json")))
    print(json.dumps(aggregates, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-seed50-training", action="store_true")
    args = parser.parse_args()
    os.chdir(RUN.parent / "baseline_prorl")
    os.environ.update(ENV="test", FILTER_PATH="", DATA_BASE_DIR="data")
    import sys
    sys.path.insert(0, os.getcwd())
    torch.set_num_threads(1)
    if args.verify_seed50_training:
        audit, _ = verify_training(50)
        write("seed50_completion_verification.json", audit)
        print(json.dumps(audit, indent=2))
    else:
        compare()
