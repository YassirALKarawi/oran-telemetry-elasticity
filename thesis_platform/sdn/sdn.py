"""Apply a decoded E2 share using OpenFlow 1.3 and independently measure delivery."""
import json
import os
import re
import statistics
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "transport_shares"))
import trial

OUT = trial.OUT
TARGET = "tcp:127.0.0.1:16653"
IPS = trial.IPS


def command(*args):
    return subprocess.check_output(["sudo", *args], text=True)


def of(*args):
    return command("ovs-ofctl", "-O", "OpenFlow13", args[0], TARGET, *args[1:])


def setup():
    command("ovs-vsctl", "add-br", "sdn-br", "--", "set", "bridge", "sdn-br",
            "protocols=OpenFlow13", "fail_mode=secure")
    command("ovs-vsctl", "set-controller", "sdn-br", "ptcp:16653:127.0.0.1")
    command("ip", "netns", "add", "sink")
    for port, end, number in [("sw-in", "share0", "1"), ("sw-out", "peer", "2")]:
        command("ip", "link", "add", port, "type", "veth", "peer", "name", end)
        command("ip", "link", "set", port, "up")
        command("ovs-vsctl", "add-port", "sdn-br", port, "--", "set", "interface",
                port, "ofport_request=" + number)
        assert command("ovs-vsctl", "get", "interface", port, "ofport").strip() == number
    command("ip", "link", "set", "peer", "netns", "sink")
    for i, ip in enumerate(IPS):
        command("ip", "addr", "add", f"198.18.{10+i}.1/30", "dev", "share0")
        command("ip", "-n", "sink", "addr", "add", ip + "/30", "dev", "peer")
    command("ip", "link", "set", "share0", "up")
    command("ip", "-n", "sink", "link", "set", "peer", "up")
    trial.LINKS = ["share0", "sw-out"]  # actual egress qdisc backlog, before and after switching
    of("show")
    meters(10, "add")
    for i, ip in enumerate(IPS, 1):
        of("add-flow", f"priority=200,in_port=1,udp,nw_dst={ip},tp_dst=8940,actions=meter:{i},output:2")
    of("add-flow", "priority=10,in_port=1,actions=output:2")
    of("add-flow", "priority=10,in_port=2,actions=output:1")
    for ip in IPS:
        command("ping", "-c", "1", "-W", "2", ip)


def meters(share, operation):
    config = []
    for i, units in enumerate([share, 20-share], 1):
        rate = units * 800
        of(operation + "-meter", f"meter={i},kbps,burst,stats,bands=type=drop,rate={rate},burst_size=64")
        state = of("dump-meters", str(i))
        assert f"rate={rate}," in state
        config.append(state)
    (OUT / f"meters-{operation}.txt").write_text("".join(config))


def phase(label):
    def counters(tag):
        vals = []
        for i in [1, 2]:
            stats = of("meter-stats", str(i))
            (OUT / f"{label}-{tag}-meter-{i}.txt").write_text(stats)
            vals.append([int(re.search(r"packet_in_count[=:]\s*(\d+)", stats).group(1)),
                         int(re.search(r"packet_count[=:]\s*(\d+)", stats).group(1))])
        (OUT / f"{label}-{tag}-flows.txt").write_text(of("dump-flows"))
        return vals
    start = counters("start")
    rows = [trial.traffic([18, 10]) for _ in range(3)]
    end = counters("end")
    delta = [[b-a for a,b in zip(x,y)] for x,y in zip(start,end)]
    for i, (packets, drops) in enumerate(delta):
        sent = sum(r["sent"][i] for r in rows)
        received = sum(r["received"][i] for r in rows)
        assert packets == sent and 0 < drops <= sent-received
    summary = dict(rows=rows, meter_deltas=delta, receiver_mbps=[
        statistics.median(r["received"][i]*0.008/r["elapsed"] for r in rows) for i in range(2)])
    (OUT / f"{label}.json").write_text(json.dumps(summary, indent=2))
    return summary


def run():
    setup()
    before = phase("before")
    selected, report, _ = trial.decide(before["rows"][-1], 0)
    guarded = min(12, selected)
    assert 1 <= guarded <= 19 and guarded != 10
    exe = next(Path("build").rglob("xapp_mac_ctrl"))
    with (OUT/"control.log").open("w") as log:
        subprocess.run([exe], env={**os.environ,"E2_SHARE":str(guarded)}, stdout=log,
                       stderr=subprocess.STDOUT, check=True, timeout=20)
    assert "CONTROL ACK rx" in (OUT/"control.log").read_text()
    decoded = list(map(int, Path(os.environ["E2_SHARE_EVENTS"]).read_text().splitlines()))
    assert decoded == [guarded]
    meters(decoded[0], "mod")
    after = phase("after")
    for i, direction in enumerate([guarded-10, 10-guarded]):
        assert direction*(after["receiver_mbps"][i]-before["receiver_mbps"][i]) > 0
    (OUT/"decision.json").write_text(json.dumps(dict(selected=selected, guarded=guarded,
        report=report, decoded=decoded, before=before["receiver_mbps"], after=after["receiver_mbps"]),indent=2))


if __name__ == "__main__":
    run()
