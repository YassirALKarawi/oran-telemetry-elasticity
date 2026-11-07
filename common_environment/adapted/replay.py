"""Verify all held-out outcomes from the saved validation-selected models."""
from train_adapted import Adapter, OUT, P, inputs, run, digest
import base64
import hashlib
import io
import json
import torch
import zlib

record=json.loads((OUT/"results.json").read_text())
models={}
for key,encoded in json.loads((OUT/"models.json").read_text()).items():
    raw=zlib.decompress(base64.b64decode(encoded))
    assert hashlib.sha256(raw).hexdigest()==record["selection"][key]["sha256"]
    net=Adapter(int(key))
    net.net.load_model(torch.load(io.BytesIO(raw),weights_only=True))
    net.training=False
    models[key]=net

for row in record["traces"]:
    args=inputs(row["trace_seed"],row["scenario"])
    assert digest(args)==row["trace_sha256"]
    for key,expected in row["results"].items():
        actual=run(key,*args,controller=models.get(key),write_logs=False)
        assert expected==actual,(row["trace_seed"],key)
print("Replayed 15 traces x 7 policies/checkpoints; all recorded outcomes matched.")
