import hashlib
import json
import statistics
import sys
import zipfile
from pathlib import Path


def audit(archive):
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        protocol = json.loads(z.read("protocol.json"))
        rows = [json.loads(s) for s in z.read("holdout.jsonl").splitlines()]
        events = list(map(int,z.read("agent-actions.txt").splitlines()))
        frames = z.read("frames.tsv").lower()
        assert frames.count(b'riccontrolrequest') == frames.count(b'riccontrolacknowledge') == 60
        assert len(rows) == 72
        pending = iter(rows)
        verified = []
        results = []
        for trace in protocol["traces"]:
            metrics = {}
            for method in trace["order"]:
                active = 10
                sent, got = [0,0],[0,0]
                switch_sent = switch_got = 0
                previous = None
                for epoch,rates in enumerate(trace["rates_mbps"]):
                    row = next(pending)
                    assert (row['seed'],row['method'],row['epoch'],row['rates'],row['active']) == (trace['seed'],method,epoch,rates,active)
                    assert row['sent'] == [x*250 for x in rates]
                    for i in range(2):
                        assert 0<row['received'][i]<=row['sent'][i]
                        sent[i]+=row['sent'][i]
                        got[i]+=row['received'][i]
                    heavy = rates[0]>rates[1]
                    if previous is not None and heavy!=previous:
                        switch_got += sum(row['received'])
                        switch_sent += sum(row['sent'])
                    previous=heavy
                    if epoch<5:
                        selected = row[method]
                        if method=='proportional':
                            total=sum(row['sent'])
                            assert selected==max(1,min(19,(40*row['sent'][0]+total)//(2*total)))
                        assert row['applied_next'] == [selected,20-selected]
                        assert b'CONTROL ACK rx' in z.read(f"control-{trace['seed']}-{method}-{epoch}.log")
                        verified.append(selected)
                        active=selected
                metrics[method]=dict(sent=sent,received=got,overall=100*sum(got)/sum(sent),
                                     class1=100*got[0]/sent[0],class2=100*got[1]/sent[1],
                                     transition=100*switch_got/switch_sent)
            assert metrics['thesis']['sent']==metrics['proportional']['sent']
            results.append(dict(seed=trace['seed'],family=trace['family'],**metrics))
        assert verified==events
    fields=['overall','class1','class2','transition']
    means={p:{f:statistics.mean(r[p][f] for r in results) for f in fields} for p in ('thesis','proportional')}
    return dict(sha256=hashlib.sha256(Path(archive).read_bytes()).hexdigest(),traces=results,means=means)


if __name__=='__main__':
    print(json.dumps(audit(sys.argv[1]),indent=2))
