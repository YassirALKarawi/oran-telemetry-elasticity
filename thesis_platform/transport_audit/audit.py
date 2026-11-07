"""Audit the two zipped CI evidence bundles without executing their contents."""
import collections
import hashlib
import json
from pathlib import Path
import re
import statistics
import struct
import sys
import zipfile


def verify_factorial(archive):
    with zipfile.ZipFile(archive) as z:
        protocol = json.loads(z.read("protocol.json"))
        rows = [json.loads(s) for s in z.read("factorial.jsonl").splitlines()]
        issued = list(map(int, z.read("agent-actions.txt").splitlines()))
        frames = z.read("frames.tsv").decode().lower()
        published = json.loads(z.read("factorial-scores.json"))
    assert len(rows) == 160 and len(issued) == 128
    assert frames.count("riccontrolrequest") == frames.count("riccontrolacknowledge") == 128
    assert len({t["seed"] for t in protocol["traces"]}) == 8
    groups = collections.defaultdict(list)
    index = 0
    actions = []
    for trace in protocol["traces"]:
        assert set(trace["order"]) == {"thesis", "thesis_floor", "proportional", "proportional_floor"}
        for method in trace["order"]:
            active = 10
            totals = [0, 0]
            timely = [0, 0]
            for epoch, rates in enumerate(trace["rates_mbps"]):
                row = rows[index]
                index += 1
                assert (row["seed"],row["method"],row["epoch"],row["active"]) == (trace["seed"],method,epoch,active)
                assert row["rates"] == rates and row["sent"] == [250*v for v in rates]
                for i, deadline in enumerate(protocol["deadlines_ms"]):
                    hist = row["delay_ms_ceiling_histogram"][i]
                    assert sum(hist.values()) == row["received"][i] <= row["sent"][i]
                    timely[i] += sum(n for k,n in hist.items() if int(k) <= deadline)
                    totals[i] += row["sent"][i]
                if epoch < 4:
                    a,b = row["sent"]
                    prop = max(1,min(19,(40*a+a+b)//(2*(a+b))))
                    assert prop == row["proportional"]
                    active = row["thesis"] if method.startswith("thesis") else prop
                    if method.endswith("_floor"):
                        active = min(active,12)
                    assert row["applied_next"] == [active,20-active]
                    actions.append(active)
            groups[method].append([100*a/b for a,b in zip(timely+[sum(timely)],totals+[sum(totals)])])
    assert actions == issued
    for method, vectors in groups.items():
        means = list(map(statistics.mean,zip(*vectors)))
        assert means == published[method]["means"]
        print(method, means)
    for left,right in [("thesis_floor","proportional_floor"),("thesis","proportional"),("thesis_floor","thesis"),("proportional_floor","proportional")]:
        diffs = [a[2]-b[2] for a,b in zip(groups[left],groups[right])]
        print(left,right,diffs,statistics.mean(diffs))


def meter_commands(pcap):
    # tcpdump on the runner records Ethernet, IPv4, TCP. Group TCP segments
    # by client port and sequence number before decoding OpenFlow messages.
    assert pcap[:4] == bytes.fromhex("d4c3b2a1") and struct.unpack_from("<I",pcap,20)[0] == 1
    streams = collections.defaultdict(dict)
    offset = 24
    while offset < len(pcap):
        caplen = struct.unpack_from("<I",pcap,offset+8)[0]
        frame = pcap[offset+16:offset+16+caplen]
        offset += 16 + caplen
        if frame[12:14] != b"\x08\x00" or frame[23] != 6:
            continue
        ip_length = int.from_bytes(frame[16:18],"big")
        tcp = frame[14+(frame[14]&15)*4:14+ip_length]
        src,dst,seq = struct.unpack_from("!HHI",tcp)
        payload = tcp[(tcp[12] >> 4)*4:]
        if dst == 16653 and payload:
            streams[src][seq] = payload
    commands = []
    for segments in streams.values():
        blob = b"".join(segments[k] for k in sorted(segments))
        cursor = 0
        while cursor < len(blob):
            version,kind,size = struct.unpack_from("!BBH",blob,cursor)
            assert size >= 8 and cursor+size <= len(blob)
            if version == 4 and kind == 29:
                command,flags,meter,band,length,rate,burst = struct.unpack_from("!HHIHHII",blob,cursor+8)
                assert flags == 13 and band == 1 and length == 16 and burst == 64
                commands.append((command,meter,rate))
            cursor += size
    return sorted(commands)


def verify_sdn(archive):
    with zipfile.ZipFile(archive) as z:
        d = json.loads(z.read("decision.json"))
        share = int(z.read("agent-actions.txt"))
        assert share == min(12,d["selected"]) == d["guarded"]
        frames = z.read("frames.tsv").decode().lower()
        assert frames.count("riccontrolrequest") == frames.count("riccontrolacknowledge") == 1
        assert meter_commands(z.read("control.pcap")) == sorted([
            (0,1,8000),(0,2,8000),(1,1,share*800),(1,2,(20-share)*800)])
        for phase, units, op in [("before",10,"add"),("after",share,"mod")]:
            data = json.loads(z.read(phase+".json"))
            assert len(data["rows"]) == 3
            for i, u in enumerate([units,20-units]):
                assert re.search(rf"\brate={u*800}\b", z.read("meters-"+op+".txt").decode())
                sent = sum(row["sent"][i] for row in data["rows"])
                received = sum(row["received"][i] for row in data["rows"])
                counted,dropped = data["meter_deltas"][i]
                raw = []
                for tag in ["start","end"]:
                    raw_stats = z.read(f"{phase}-{tag}-meter-{i+1}.txt").decode()
                    raw.append([int(re.search(key+r"[:=]\s*(\d+)",raw_stats).group(1))
                                for key in ["packet_in_count","packet_count"]])
                assert [b-a for a,b in zip(*raw)] == [counted,dropped]
                assert sent == counted and 0 < dropped <= sent-received
                median = statistics.median(row["received"][i]*.008/row["elapsed"] for row in data["rows"])
                assert median == d[phase][i]
            print(phase,data["meter_deltas"],data["receiver_mbps"])
        print("e2 share",share)


if __name__ == "__main__":
    for filename, verify in zip(sys.argv[1:], [verify_factorial,verify_sdn],strict=True):
        p = Path(filename)
        print(p.name,hashlib.sha256(p.read_bytes()).hexdigest())
        verify(p)
