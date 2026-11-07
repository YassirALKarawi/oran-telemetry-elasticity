"""Train nested budgets, evaluate frozen models, or replay saved outcomes."""
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import statistics
import subprocess
import sys
import zlib

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from train_adapted import Adapter, P, deploy, digest, freeze, inputs, run, torch

SPEC = json.loads((HERE / "protocol.json").read_text())
BUDGETS = SPEC["budget_episodes"]


def write(name, data):
    path = HERE / name
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, separators=(",", ":"), allow_nan=False) + "\n")
    tmp.replace(path)


def unpack(encoded):
    return zlib.decompress(base64.b64decode(encoded, validate=True))


def state(raw):
    return torch.load(io.BytesIO(raw), map_location="cpu", weights_only=True)


def train():
    previous = json.loads((HERE.parent / "models.json").read_text())
    original = json.loads((HERE.parent / "results.json").read_text())["selection"]
    for seed in P["training_seeds"]:
        agent = Adapter(seed)
        scores, candidates, selected = {}, {}, {}
        for episode in range(1, max(BUDGETS) + 1):
            agent.training = True
            i = episode - 1
            deploy(agent, 910000 + i, P["scenarios"][i % 3])
            if episode not in BUDGETS and 2 * episode not in BUDGETS:
                continue
            agent.training = False
            scores[episode] = [deploy(agent, 920000 + j, sc)["total_cost"]
                               for j, sc in enumerate(P["scenarios"])]
            candidates[episode] = freeze(agent)
            if episode in BUDGETS:
                index = BUDGETS.index(episode)
                assert agent.steps == SPEC["budget_decisions"][index]
                best = min([episode // 2, episode], key=lambda e: (statistics.mean(scores[e]), e))
                raw = candidates[best]
                tensors = state(raw)
                assert all(torch.isfinite(v).all() for v in tensors.values())
                if episode == BUDGETS[0]:
                    old = state(unpack(previous[str(seed)]))
                    assert best == original[str(seed)]["episode"]
                    assert tensors.keys() == old.keys() and all(torch.equal(v, old[k]) for k,v in tensors.items())
                selected[episode] = dict(episode=best, decisions=agent.steps,
                                         sha256=hashlib.sha256(raw).hexdigest(),
                                         model=base64.b64encode(zlib.compress(raw)).decode())
        write(f"seed{seed}.json", dict(seed=seed, scores=scores, selected=selected))
        print("Frozen budgets for seed", seed, flush=True)


def evaluate(replay):
    agents = {}
    for seed in P["training_seeds"]:
        saved = json.loads((HERE / f"seed{seed}.json").read_text())
        for budget in BUDGETS:
            model = saved["selected"][str(budget)]
            raw = unpack(model["model"])
            assert hashlib.sha256(raw).hexdigest() == model["sha256"]
            agent = Adapter(seed)
            agent.net.load_model(state(raw))
            agent.training = False
            agents[f"{budget}/{seed}"] = agent
    for sc, seeds in SPEC["test_seeds"].items():
        rows = []
        for seed in seeds:
            events, loss = inputs(seed, sc)
            outcomes = {name:run(name,events,loss,write_logs=False) for name in ("thesis","greedy")}
            for name, agent in agents.items():
                outcomes[name] = run("adapted",events,loss,controller=agent,write_logs=False)
            assert len({v["offered"] for v in outcomes.values()}) == 1
            for v in outcomes.values():
                assert v["offered"] == v["delivered"] + v["outstanding"] + v["lost"]
                assert all(x <= y for x,y in zip(v["stage_service"], v["stage_supply"]))
            rows.append(dict(seed=seed, trace_sha256=digest([events,loss]), outcomes=outcomes))
        filename = sc + ".json"
        if replay:
            assert rows == json.loads((HERE / filename).read_text())
        else:
            write(filename, rows)
        print("Replayed" if replay else "Evaluated", sc, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["train", "test", "replay"])
    phase = parser.parse_args().phase
    assert subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip() == P["source"]
    assert hashlib.sha256(subprocess.check_output(["git","diff","HEAD"])).hexdigest() == P["diff_sha256"]
    if phase == "train":
        train()
    else:
        evaluate(phase == "replay")
