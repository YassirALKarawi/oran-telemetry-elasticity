"""Transport-only actuator check on Linux loopback. Run from any directory."""
import argparse
from collections import deque
import json
from pathlib import Path
import select
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from elastic import solve_elastic

HOST = "127.0.0.1"
N = 700
BASE = 120
UNIT = 40
NS = 1_000_000_000
clock = time.monotonic_ns


def udp():
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.bind((HOST,0))
    s.settimeout(2)
    return s


def forward(port):
    queue = deque()
    counts = [0,0]
    received = sent = 0
    rate = 0
    next_send = 0
    with udp() as ingress:
        print(ingress.getsockname()[1],flush=True)
        while True:
            wait = max(0,(next_send-clock())/NS) if rate and queue else 2
            if select.select([ingress],[],[],wait)[0]:
                data, peer = ingress.recvfrom(2048)
                if data.startswith(b"P"):
                    sequence = int.from_bytes(data[1:5],"big")
                    queue.append((sequence,data))
                    counts[sequence%2] += 1
                    received += 1
                else:
                    command = json.loads(data)
                    stamp = clock()
                    if command["kind"] == "set":
                        extra = command["extra"]
                        assert extra in range(4)
                        rate = BASE + UNIT*extra
                        next_send = stamp
                    reply = dict(id=command["id"],observed_ns=stamp,queued=counts,
                                 received=received,sent=sent,rate=rate)
                    ingress.sendto(json.dumps(reply).encode(),peer)
                    if command["kind"] == "stop":
                        return
            if rate and queue and clock() >= next_send:
                k,data=queue.popleft()
                ingress.sendto(data,(HOST,port))
                counts[k%2] -= 1
                sent += 1
                next_send=clock()+round(NS/rate)


def trial():
    with udp() as control, udp() as sink, udp() as source, subprocess.Popen(
        [sys.executable,__file__,"--forward",str(sink.getsockname()[1])],
        stdout=subprocess.PIPE,text=True) as child:
        try:
            peer=(HOST,int(child.stdout.readline()))
            messages=[]
            def ask(kind,**fields):
                msg=dict(id=len(messages),kind=kind,**fields)
                issued=clock()
                control.sendto(json.dumps(msg).encode(),peer)
                data,addr=control.recvfrom(2048)
                ack=json.loads(data)
                assert addr==peer and ack["id"]==msg["id"]
                messages.append(dict(command=msg,issued_ns=issued,ack_ns=clock(),reply=ack))
                return ack

            for k in range(N):
                source.sendto(b"P"+k.to_bytes(4,"big")+bytes(123),peer)
                if k%12==0:
                    time.sleep(.001)
            for _ in range(20):
                if ask("read")["received"]==N:
                    break
                time.sleep(.01)
            assert messages[-1]["reply"]["received"]==N
            receipts=[]
            phases=[]
            for phase in ("baseline","thesis_transport","reset"):
                telemetry=ask("read")
                extra=0
                target=None
                if phase=="thesis_transport":
                    reports=[dict(q=[0,0],arrival=[1,1],service=[1,1],variance=[0,0],
                                  capacity=5,time=0) for _ in range(3)]
                    reports[1].update(q=telemetry["queued"],capacity=3)
                    target=solve_elastic(reports,0,[0,0,0])[0]
                    extra=target[1]
                applied=ask("set",extra=extra)
                start=applied["observed_ns"]
                end=start+int(.8*NS)
                while clock()<end:
                    if select.select([sink],[],[],max(0,(end-clock())/NS))[0]:
                        packet,_=sink.recvfrom(2048)
                        receipts.append((int.from_bytes(packet[1:5],"big"),clock(),len(packet)))
                count=sum(start+int(.1*NS)<=t<end-int(.1*NS) for _,t,_ in receipts)
                phases.append(dict(name=phase,target=target,extra=extra,applied_ns=start,
                                   measured_pps=count/.6,window_packets=count))
            final=ask("stop")
            child.wait(timeout=3)
            while select.select([sink],[],[],.02)[0]:
                packet,_=sink.recvfrom(2048)
                receipts.append((int.from_bytes(packet[1:5],"big"),clock(),len(packet)))
            seq=[k for k,_,_ in receipts]
            assert child.returncode==0 and seq==list(range(final["sent"]))
            assert all(n==128 for _,_,n in receipts)
            assert final["received"]==N==len(seq)+sum(final["queued"]) and sum(final["queued"])>0
            return dict(phases=phases,messages=messages,receipts=receipts,offered=N,
                        delivered=len(seq),outstanding=sum(final["queued"]))
        finally:
            if child.poll() is None:
                child.terminate()


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--forward",type=int)
    args=parser.parse_args()
    if args.forward:
        forward(args.forward)
    else:
        runs=[trial() for _ in range(3)]
        path=Path(__file__).with_name("observations.json")
        path.write_text(json.dumps(runs,separators=(",",":"))+"\n")
        for row in runs:
            print([round(p["measured_pps"],1) for p in row["phases"]],row["delivered"],row["outstanding"])
