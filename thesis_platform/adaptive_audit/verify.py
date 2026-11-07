"""Recompute the adaptive trial measurements from archived CI evidence."""
import json
import struct
import math
import re
import statistics
import sys
import zipfile
from pathlib import Path
from collections import defaultdict


def events(z, expected):
    decoded = list(map(int,z.read("agent-actions.txt").splitlines()))
    assert decoded == expected
    frames = z.read("frames.tsv").lower()
    assert frames.count(b"riccontrolrequest") == frames.count(b"riccontrolacknowledge") == len(expected)


def selection(method,row):
    a,b = row["sent"]
    proportional = max(1,min(12,(40*a+a+b)//(2*(a+b))))
    thesis = max(1,min(12,row["thesis"]))
    if method == "proportional_floor":
        return proportional
    if method == "adaptive" and 100*(b-row["received"][1]) >= 5*b:
        return min(thesis,proportional)
    return thesis


def compare(z):
    protocol = json.loads(z.read("protocol.json"))
    records = list(map(json.loads,z.read("factorial.jsonl").splitlines()))
    assert len(records)==90
    expected=[]
    scores=defaultdict(list)
    k=0
    for trace in protocol["traces"]:
        for method in trace["order"]:
            active=10
            sent=[0,0]
            timely=[0,0]
            for epoch,rates in enumerate(trace["rates_mbps"]):
                r=records[k]
                k+=1
                assert (r["method"],r["seed"],r["epoch"],r["active"]) == (method,trace["seed"],epoch,active)
                assert rates==r["rates"] and r["sent"]==[v*250 for v in rates]
                for i,deadline in enumerate(protocol["deadlines_ms"]):
                    hist=r["delay_ms_ceiling_histogram"][i]
                    assert sum(hist.values())==r["received"][i]<=r["sent"][i]
                    timely[i]+=sum(v for t,v in hist.items() if int(t)<=deadline)
                    sent[i]+=r["sent"][i]
                active=selection(method,r)
                assert active==r["selected"]
                if epoch<4:
                    assert r["applied_next"]==[active,20-active]
                    expected.append(active)
            scores[method].append([100*x/y for x,y in zip(timely+[sum(timely)],sent+[sum(sent)])])
    events(z,expected)
    summary={key:list(map(statistics.mean,zip(*rows))) for key,rows in scores.items()}
    archived=json.loads(z.read("factorial-scores.json"))
    assert all(summary[k]==archived[k]["means"] for k in scores)
    return scores,summary


def meter_commands(pcap):
    # tcpdump on the runner records Ethernet, IPv4, TCP. Group TCP segments
    # by client port and sequence number before decoding OpenFlow messages.
    assert pcap[:4] == bytes.fromhex("d4c3b2a1") and struct.unpack_from("<I",pcap,20)[0] == 1
    streams = defaultdict(dict)
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


def switching(z):
    records=list(map(json.loads,z.read("switch.jsonl").splitlines()))
    loads=json.loads(z.read("protocol.json"))["switch_loads"]
    assert len(records)==len(loads)==12
    active=10
    expected=[]
    output=[]
    for k,(row,rates) in enumerate(zip(records,loads)):
        assert row["active"]==active and row["epoch"]==k and row["rates"]==rates
        for i in range(2):
            stats=[]
            for tag in ["start","end"]:
                raw=z.read(f"{k}-{tag}-meter-{i+1}.txt").decode()
                stats.append([int(re.search(key+r"[:=]\s*(\d+)",raw).group(1))
                              for key in ["packet_in_count","packet_count"]])
            packets,drops=[b-a for a,b in zip(*stats)]
            assert packets==rates[i]*250==row["sent"][i] and 0<=drops<=packets-row["received"][i]
        obs=dict(epoch=k,active=active,receiver=[n*.008/row["elapsed"] for n in row["received"]])
        if k<11:
            active=selection("adaptive",row)
            assert active==row["selected"]
            raw=z.read(f"meters-{k}.txt").decode()
            assert [int(v) for v in re.findall(r"\brate=(\d+)\b",raw)]==[800*active,800*(20-active)]
            elapsed=row["command_to_readback_s"]
            assert math.isfinite(elapsed) and elapsed>0
            obs.update(selected=active,elapsed=elapsed)
            expected.append(active)
        output.append(obs)
    events(z,expected)
    commands=[(0,1,8000),(0,2,8000)]
    for share in expected:
        commands.extend([(1,1,800*share),(1,2,800*(20-share))])
    assert meter_commands(z.read("control.pcap"))==sorted(commands)
    return output


if __name__=="__main__":
    with zipfile.ZipFile(sys.argv[1]) as f, zipfile.ZipFile(sys.argv[2]) as s:
        assert f.read("protocol.json")==s.read("protocol.json")
        paired,means=compare(f)
        print(json.dumps(dict(paired=paired,means=means,switch=switching(s)),indent=2))
