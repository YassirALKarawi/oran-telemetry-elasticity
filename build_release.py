"""Verify the study, retain test receipts, hash deliverables and build archive."""
import datetime
import hashlib
import json
import subprocess
import sys
import os
import tempfile
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent
commands=[
    [sys.executable,'-m','unittest','baseline.simulate','experiment','evaluate_v3','evaluate_v4',
     'independent_validation','verify_extension','test_pipeline','test_reliability','-v'],
    [sys.executable,'verify_frozen.py'],
    [sys.executable,'verify_extension.py'],
    [sys.executable,'verify_paper.py'],
    [sys.executable,'verify_reliability.py'],
    [sys.executable,'verify_manuscript.py'],
    [sys.executable,'verify_substantive.py'],
    [sys.executable,'verify_advanced_model.py'],
    [sys.executable,'verify_journal_revision.py'],
]
receipts=[]
for command in commands:
    result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    receipts.append(dict(command=command,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr))
    if result.returncode:
        raise RuntimeError(result.stdout+result.stderr)
(ROOT/'verification_receipt.json').write_text(json.dumps(dict(
    checked_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=receipts),indent=2))

def include(p):
    return (p.is_file() and '__pycache__' not in p.parts and
            p.name not in ('SHA256.json','extension_checkpoint.json','paper_checkpoint.json','reliability_test_checkpoint.json') and
            not (p.parent.name=='paper_reliability' and p.suffix=='.png') and
            p.suffix not in ('.aux','.log','.out','.toc'))

files=sorted(p for p in ROOT.rglob('*') if include(p))
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(ROOT/'SHA256.json').write_text(json.dumps(hashes,indent=2))
archive=ROOT.parent/'ORAN_Telemetry_Pilot.zip'
fd,staging_name=tempfile.mkstemp(prefix='release-',suffix='.zip',dir=ROOT.parent)
os.close(fd)
staging=Path(staging_name)
with zipfile.ZipFile(staging,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files+[ROOT/'SHA256.json']:
        z.write(p,'oran_study/'+str(p.relative_to(ROOT)))
with zipfile.ZipFile(staging) as z:
    assert z.testzip() is None
    for name,digest in hashes.items():
        assert hashlib.sha256(z.read('oran_study/'+name)).hexdigest()==digest
os.replace(staging,archive)
print(json.dumps(dict(archive=str(archive),files=len(files)+1,bytes=archive.stat().st_size,
                     tests='51 unit methods plus frozen/extension/paper/reliability verifiers',sha256_verified=True)))
