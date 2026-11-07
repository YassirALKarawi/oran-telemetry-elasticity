"""Paired transport-share experiment on two shaped Linux veth links."""
import json
import math
import os
from pathlib import Path
import selectors
import socket
import statistics
import struct
import subprocess
import sys
import time

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
from elastic import solve_elastic

OUT = ROOT / "evidence"
DURATION = 2.0
SIZE = 1000
UNIT_BPS = 800_000
WINDOW_S = 0.1
UNIT_BYTES = UNIT_BPS * WINDOW_S / 8
LINKS = ["share0", "share1"]
IPS = ["198.18.10.2", "198.18.11.2"]
# Payload rates in Mbit/s. Replay identical integer packet counts and timing.
TRACE = [(12, 3), (12, 3), (12, 3), (3, 12), (3, 12), (3, 12)]
HEADER = struct.Struct("!IQ")


def command(*args):
    return subprocess.check_output([str(x) for x in args], text=True)


def setup():
    command("sudo", "ip", "netns", "add", "sink")
    for i, dev in enumerate(LINKS):
        peer = f"peer{i}"
        command("sudo", "ip", "link", "add", dev, "type", "veth", "peer", "name", peer)
        command("sudo", "ip", "link", "set", peer, "netns", "sink")
        command("sudo", "ip", "addr", "add", f"198.18.{10+i}.1/30", "dev", dev)
        command("sudo", "ip", "-n", "sink", "addr", "add", IPS[i]+"/30", "dev", peer)
        command("sudo", "ip", "link", "set", dev, "up")
        command("sudo", "ip", "-n", "sink", "link", "set", peer, "up")


def apply(share):
    rates = [share, 20-share]
    for dev, units in zip(LINKS, rates):
        rate = units * UNIT_BPS
        command("sudo", "tc", "qdisc", "replace", "dev", dev, "root", "handle", "1:",
                "tbf", "rate", f"{rate}bit", "burst", "4000", "limit", "16000")
        state = qdisc(dev)
        assert state["options"]["rate"] * 8 == rate
    return rates


def qdisc(dev):
    return json.loads(command("tc", "-s", "-j", "qdisc", "show", "dev", dev))[0]


def receiver():
    sel = selectors.DefaultSelector()
    seen = [set(), set()]
    delays = [[], []]
    for i, ip in enumerate(IPS):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((ip, 8940))
        sel.register(sock, selectors.EVENT_READ, i)
    print("READY", flush=True)
    while True:
        events = sel.select(1.0)
        if not events:
            break
        for key, _ in events:
            payload = key.fileobj.recv(2048)
            seq, sent = HEADER.unpack_from(payload)
            i = key.data
            assert len(payload) == SIZE and seq not in seen[i]
            seen[i].add(seq)
            delays[i].append((time.monotonic_ns()-sent)/1e6)
    print(json.dumps(dict(received=[len(x) for x in seen],
                          p95_ms=[sorted(d)[math.ceil(.95*len(d))-1] if d else None for d in delays])))


def traffic(rates):
    counts = [int(r*1e6*DURATION/(8*SIZE)) for r in rates]
    schedule = sorted((j*DURATION/n, i, j) for i,n in enumerate(counts) for j in range(n))
    with subprocess.Popen(["sudo","ip","netns","exec","sink",sys.executable,__file__,"sink"],
                          stdout=subprocess.PIPE,text=True) as sink:
        assert sink.stdout.readline().strip() == "READY"
        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
            start = time.monotonic()
            samples = []
            for offset,i,j in schedule:
                due = start + offset - time.monotonic()
                if due > 0:
                    time.sleep(due)
                sock.sendto(HEADER.pack(j,time.monotonic_ns()) + bytes(SIZE-HEADER.size), (IPS[i],8940))
                if offset >= .4*(len(samples)+1) and len(samples)<4:
                    samples.append([qdisc(d)["backlog"] for d in LINKS])
            elapsed = time.monotonic()-start
        line,_ = sink.communicate(timeout=5)
        assert sink.returncode == 0
    result = json.loads(line)
    assert all(0 < n <= m for n,m in zip(result["received"],counts))
    result.update(sent=counts, elapsed=elapsed, backlog_bytes=samples)
    return result


def decide(row, epoch):
    def units(counts):
        return [n*SIZE/row["elapsed"]*WINDOW_S/UNIT_BYTES for n in counts]
    report = dict(capacity=20,time=epoch,q=[statistics.mean(col)/UNIT_BYTES for col in zip(*row["backlog_bytes"])],
                  arrival=units(row["sent"]),service=units(row["received"]),variance=[0,0])
    idle = dict(capacity=100,time=epoch,q=[0,0],arrival=[0,0],service=[0,0],variance=[0,0])
    _, weights, audit = solve_elastic([idle,report,idle],epoch,[0,0,0],fixed=(0,0,0),delay=1)
    return round(20*weights[1][0]), report, audit


def run():
    setup()
    exe = next(Path("build").rglob("xapp_mac_ctrl"))
    events = Path(os.environ["E2_SHARE_EVENTS"])
    results = []
    event_count = 0
    for pair,method in [(1,"thesis"),(1,"equal"),(2,"equal"),(2,"thesis")]:
        active = 10
        apply(active)
        for epoch, rates in enumerate(TRACE):
            result = traffic(rates)
            row = dict(pair=pair,method=method,epoch=epoch,active_share=active,**result)
            candidate,report,audit = decide(result,epoch)
            row.update(report=report,shadow_thesis_share=candidate,solver=audit)
            if epoch+1 < len(TRACE):
                selected = candidate if method=="thesis" else 10
                log = OUT / f"control-{pair}-{method}-{epoch}.log"
                with log.open("w") as out:
                    subprocess.run([exe],env={**os.environ,"E2_SHARE":str(selected)},stdout=out,
                                   stderr=subprocess.STDOUT,timeout=15,check=True)
                assert "CONTROL ACK rx" in log.read_text()
                decoded = [int(x) for x in events.read_text().splitlines()]
                event_count += 1
                assert len(decoded)==event_count and decoded[-1]==selected
                row["next_units"] = apply(decoded[-1])
                active = decoded[-1]
            results.append(row)
            (OUT/"paired.json").write_text(json.dumps(results,indent=2))
    assert len({r["active_share"] for r in results if r["method"]=="thesis"})>1
    assert all(r["elapsed"] < DURATION*1.05 for r in results)


if __name__ == "__main__":
    if sys.argv[1:] == ["sink"]:
        receiver()
    else:
        run()
