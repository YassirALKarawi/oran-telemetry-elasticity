#!/usr/bin/env python3
"""Recompute and verify two frozen independent-validation evidence archives."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
import zipfile
from collections import Counter
from pathlib import Path


POLICIES = ["adaptive", "thesis_floor", "proportional_floor"]
ENDPOINTS = ["class1", "class2", "combined"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def choose(method: str, thesis: int, sent: list[int], received: list[int]) -> int:
    total = sum(sent)
    proportional = (40 * sent[0] + total) // (2 * total)
    baseline = max(1, min(12, proportional))
    guarded = max(1, min(12, thesis))
    if method == "proportional_floor":
        return baseline
    if method == "adaptive":
        if sent[1] > 0 and 100 * (sent[1] - received[1]) >= 5 * sent[1]:
            return min(guarded, baseline)
        return guarded
    if method == "thesis_floor":
        return guarded
    raise AssertionError(f"unknown policy {method}")


def find(root: Path, name: str) -> Path:
    matches = list(root.rglob(name))
    assert len(matches) == 1, (name, matches)
    return matches[0]


def find_optional(root: Path, name: str) -> Path | None:
    matches = list(root.rglob(name))
    assert len(matches) <= 1, (name, matches)
    return matches[0] if matches else None


def load_archive(zip_path: Path, extract_root: Path) -> dict:
    assert zipfile.is_zipfile(zip_path), zip_path
    target = extract_root / zip_path.stem
    target.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(target)
    return {
        "zip": zip_path,
        "zip_sha256": sha256(zip_path),
        "root": target,
        "protocol_path": find(target, "independent_protocol.json"),
        "ledger_path": find(target, "independent.jsonl"),
        "scores_path": find(target, "independent-scores.json"),
        "host_path": find(target, "host.json"),
        "actions_path": find(target, "agent-actions.txt"),
        "frames_path": find_optional(target, "frames.tsv"),
        "pcap_path": find(target, "control.pcap"),
        "revision_path": find(target, "flexric-revision.txt"),
        "patch_path": find(target, "experiment.patch"),
    }


def trace_rates(windows: list[dict], deadlines: list[int]) -> tuple[list[float], list[dict]]:
    counts = []
    for index, deadline in enumerate(deadlines):
        sent = sum(row["sent"][index] for row in windows)
        received = sum(row["received"][index] for row in windows)
        timely = 0
        for row in windows:
            histogram = row["delay_ms_ceiling_histogram"][index]
            assert sum(histogram.values()) == row["received"][index]
            timely += sum(value for ceiling, value in histogram.items()
                          if int(ceiling) <= deadline)
        assert 0 <= timely <= received <= sent
        counts.append({"sent": sent, "timely": timely,
                       "late": received - timely, "missing": sent - received})
    rates = [100 * item["timely"] / item["sent"] for item in counts]
    rates.append(100 * sum(item["timely"] for item in counts)
                 / sum(item["sent"] for item in counts))
    return rates, counts


def recompute(rows: list[dict], protocol: dict) -> dict:
    result = {}
    for speed in protocol["transition_speeds"]:
        result[speed] = {}
        for method in POLICIES:
            traces = []
            for seed in protocol["seeds_by_speed"][speed]:
                windows = [row for row in rows if row["speed"] == speed
                           and row["method"] == method and row["seed"] == seed]
                windows.sort(key=lambda row: row["epoch"])
                assert [row["epoch"] for row in windows] == list(range(8))
                rates, counts = trace_rates(windows, protocol["deadlines_ms"])
                traces.append({"seed": seed, "counts": counts, "rates": rates})
            result[speed][method] = {
                "traces": traces,
                "means": [statistics.mean(trace["rates"][i] for trace in traces)
                          for i in range(3)],
                "sample_sd": [statistics.stdev(trace["rates"][i] for trace in traces)
                              for i in range(3)],
            }
    return result


def assert_close(actual, expected, path="root"):
    if isinstance(expected, dict):
        assert set(actual) == set(expected), (path, set(actual), set(expected))
        for key in expected:
            assert_close(actual[key], expected[key], f"{path}.{key}")
    elif isinstance(expected, list):
        assert len(actual) == len(expected), path
        for index, value in enumerate(expected):
            assert_close(actual[index], value, f"{path}[{index}]")
    elif isinstance(expected, float):
        assert math.isclose(actual, expected, rel_tol=0, abs_tol=1e-10), (path, actual, expected)
    else:
        assert actual == expected, (path, actual, expected)


def validate_host(item: dict, protocol_bytes: bytes) -> dict:
    root = item["root"]
    protocol = json.loads(protocol_bytes)
    rows = [json.loads(line) for line in item["ledger_path"].read_text().splitlines() if line]
    assert len(rows) == 432
    assert Counter(row["method"] for row in rows) == Counter({name: 144 for name in POLICIES})
    assert Counter(row["speed"] for row in rows) == Counter({name: 144 for name in protocol["transition_speeds"]})

    expected_actions = []
    trace_lookup = {(trace["speed"], trace["seed"]): trace for trace in protocol["traces"]}
    for row in rows:
        trace = trace_lookup[(row["speed"], row["seed"])]
        assert row["method"] in trace["order"]
        assert row["rates"] == trace["rates_mbps"][row["epoch"]]
        assert row["sent"] == [rate * 250 for rate in row["rates"]]
        assert 1.9 <= row["elapsed"] <= 2.1
        selected = choose(row["method"], row["thesis"], row["sent"], row["received"])
        assert row["selected"] == selected
        assert len(row["delay_ms_ceiling_histogram"]) == 2
        if row["epoch"] < 7:
            assert row["applied_next"] == [selected, 20 - selected]
            expected_actions.append(selected)

    for trace in protocol["traces"]:
        for method in trace["order"]:
            windows = [row for row in rows if row["speed"] == trace["speed"]
                       and row["seed"] == trace["seed"] and row["method"] == method]
            assert windows[0]["active"] == 10
            for before, after in zip(windows, windows[1:]):
                assert after["active"] == before["selected"]

    actions = [int(line) for line in item["actions_path"].read_text().splitlines() if line]
    assert actions == expected_actions and len(actions) == 378
    control_logs = list(root.rglob("control-*.log"))
    assert len(control_logs) == 378
    assert all("CONTROL ACK rx" in path.read_text() for path in control_logs)
    frame_gate = item["frames_path"] is not None
    if frame_gate:
        frames = item["frames_path"].read_text()
        assert len(re.findall("RICcontrolRequest", frames, re.IGNORECASE)) == 378
        assert len(re.findall("RICcontrolAcknowledge", frames, re.IGNORECASE)) == 378
    assert item["pcap_path"].stat().st_size > 0
    assert item["patch_path"].stat().st_size > 0
    revision = item["revision_path"].read_text().strip()
    assert revision == "f56d4487507c7ace392f1ec3f598e7eeda670acc"

    host = json.loads(item["host_path"].read_text())
    protocol_hash = hashlib.sha256(protocol_bytes).hexdigest()
    assert host["protocol_sha256"] == protocol_hash
    sha_line = find(root, "protocol.sha256").read_text().strip().split()[0]
    assert sha_line == protocol_hash

    recomputed = recompute(rows, protocol)
    recorded = json.loads(item["scores_path"].read_text())
    assert_close(recorded, recomputed)
    return {"host": host, "scores": recomputed,
            "packet_capture_frame_gate": "PASS" if frame_gate else "NOT_RUN_WORKFLOW_TIMEOUT",
            "counts": {"rows": len(rows), "actions": len(actions),
                       "control_logs": len(control_logs),
                       "acknowledgement_logs": len(control_logs),
                       "captured_requests": 378 if frame_gate else None,
                       "captured_acknowledgements": 378 if frame_gate else None}}


def contrasts(host_result: dict, protocol: dict) -> dict:
    output = {}
    for speed in protocol["transition_speeds"]:
        output[speed] = {}
        by_policy = host_result["scores"][speed]
        for comparator in ["proportional_floor", "thesis_floor"]:
            trace_deltas = []
            for seed in protocol["seeds_by_speed"][speed]:
                adaptive = next(t for t in by_policy["adaptive"]["traces"] if t["seed"] == seed)
                baseline = next(t for t in by_policy[comparator]["traces"] if t["seed"] == seed)
                trace_deltas.append([adaptive["rates"][i] - baseline["rates"][i]
                                     for i in range(3)])
            output[speed][f"adaptive_minus_{comparator}"] = {
                "mean": [statistics.mean(row[i] for row in trace_deltas) for i in range(3)],
                "sample_sd": [statistics.stdev(row[i] for row in trace_deltas) for i in range(3)],
                "signs": [{"positive": sum(row[i] > 1e-12 for row in trace_deltas),
                           "tied": sum(abs(row[i]) <= 1e-12 for row in trace_deltas),
                           "negative": sum(row[i] < -1e-12 for row in trace_deltas)}
                          for i in range(3)],
                "trace_deltas": trace_deltas,
            }
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path, nargs=2)
    parser.add_argument("--extract-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.extract_root.mkdir(parents=True, exist_ok=True)
    items = [load_archive(path, args.extract_root) for path in args.archive]
    protocol_bytes = items[0]["protocol_path"].read_bytes()
    assert items[1]["protocol_path"].read_bytes() == protocol_bytes
    protocol = json.loads(protocol_bytes)
    assert protocol["policies"] == POLICIES
    assert protocol["deadlines_ms"] == [15, 40]
    assert protocol["budget_mbps"] == 16 and protocol["floor_pct"] == 40

    hosts = [validate_host(item, protocol_bytes) for item in items]
    image_os = [host["host"]["image_os"] for host in hosts]
    assert len(set(image_os)) == 2 and all(value.startswith("ubuntu") for value in image_os)
    for host in hosts:
        host["contrasts"] = contrasts(host, protocol)

    cross_host = {}
    for speed in protocol["transition_speeds"]:
        cross_host[speed] = {}
        for key in hosts[0]["contrasts"][speed]:
            first = hosts[0]["contrasts"][speed][key]["mean"]
            second = hosts[1]["contrasts"][speed][key]["mean"]
            differences = [second[i] - first[i] for i in range(3)]
            cross_host[speed][key] = {
                "host2_minus_host1": differences,
                "flag_over_2pp": [abs(value) > 2 for value in differences],
            }

    frame_gates = [host["packet_capture_frame_gate"] for host in hosts]
    verification = ("PASS" if all(value == "PASS" for value in frame_gates)
                    else "PASS_WITH_DOCUMENTED_POSTPROCESSING_BLOCKER")
    output = {
        "verification": verification,
        "protocol_sha256": hashlib.sha256(protocol_bytes).hexdigest(),
        "archives": [{"name": item["zip"].name, "sha256": item["zip_sha256"]}
                     for item in items],
        "hosts": hosts,
        "cross_host_contrast_differences": cross_host,
    }
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"verification": verification, "archives": output["archives"],
                      "hosts": image_os}, indent=2))


if __name__ == "__main__":
    main()
