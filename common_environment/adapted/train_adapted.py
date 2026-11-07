"""Run from the repository using the pinned baseline_prorl interpreter."""
import base64
from collections import deque
import hashlib
import io
import json
import math
import os
from pathlib import Path
import random
import statistics
import subprocess
import sys
import zlib

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
BASE = ROOT / "baseline_prorl"
sys.path[:0] = [str(BASE), str(OUT.parent)]
os.environ.update(ENV="test", FILTER_PATH="", DATA_BASE_DIR="data")
os.chdir(BASE)
import torch
from prorl.environment.agent.dqn.double_dqn import SubAgent
from prorl.environment.agent.dqn.q_network import FullyConnected
from pilot import run, trace, digest

P = json.loads((OUT/"protocol.json").read_text())
torch.set_num_threads(1)


def features(reports,t,previous):
    values = []
    for r in reports:
        for key, scale in [("q",20),("arrival",5),("service",5),("variance",10)]:
            values.extend(x/scale for x in r[key])
        values.extend([r["capacity"]/5,(t-r["time"])/15])
    return torch.tensor(values + [previous[1]/3, previous[2]/3, t/P["slots"]], dtype=torch.float32)


class Adapter(SubAgent):
    """Retain upstream Q estimation, DDQN targets, optimizer update and target sync."""
    def __init__(self,seed):
        self.rng = random.Random(seed)
        torch.manual_seed(seed)
        self.net = FullyConnected(33,304,[32],batch_normalization=False)
        self.optimizer = torch.optim.Adam(self.net.online.parameters(),lr=0.001)
        self.gamma = 0.97
        self.is_prioritized_buffer = False
        self.buffer = deque(maxlen=2048)
        self.steps = 0
        self.last = None
        self.training = True

    def transition(self, successor, cost, terminal):
        state,action = self.last
        self.buffer.append((state,action,-cost,successor,terminal))
        if len(self.buffer)>=32:
            states,actions,rewards,successors,dones = zip(*self.rng.sample(self.buffer,32))
            estimate = self.td_estimate(torch.stack(states),torch.tensor(actions)[:,None])
            target = self.td_target(torch.tensor(rewards)[:,None],torch.stack(successors),
                                    torch.tensor(dones,dtype=torch.float32)[:,None])
            loss = self.update_Q_online(estimate,target,None)
            assert math.isfinite(loss)
        if self.steps % 80 == 0:
            self.sync_with_target_net()

    def act(self,reports,t,previous,interval_cost):
        state = features(reports,t,previous)
        if self.training and self.last is not None:
            self.transition(state,interval_cost,False)
        if self.training and self.rng.random() < max(.05,1-self.steps/900):
            index = self.rng.randrange(304)
        else:
            with torch.no_grad():
                index = int(self.net(state[None]).argmax())
        if self.training:
            self.last = state,index
            self.steps += 1
        pair,k = divmod(index,19)
        share = (k+1)/20
        return [0,pair//4,pair%4],[[share,1-share] for _ in range(3)]

    def finish(self,cost):
        if self.training:
            self.transition(torch.zeros(33),cost,True)
        self.last = None


def inputs(seed,scenario):
    events = trace(seed,P["slots"],scenario)
    rng = random.Random(seed+100000)
    drop = [rng.random()<.05 for _ in range(0,P["slots"],5)]
    return events,drop


def deploy(agent,seed,scenario):
    return run("adapted",*inputs(seed,scenario),controller=agent,write_logs=False)


def freeze(agent):
    data = io.BytesIO()
    torch.save(agent.net.online.state_dict(),data)
    return data.getvalue()


def main():
    assert subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()==P["source"]
    assert hashlib.sha256(subprocess.check_output(["git","diff","HEAD"])).hexdigest()==P["diff_sha256"]
    models,selection,weights = {},{},{}
    for seed in P["training_seeds"]:
        agent = Adapter(seed)
        candidates = []
        for i in range(P["episodes"]):
            agent.training=True
            deploy(agent,910000+i,P["scenarios"][i%3])
            if i+1 in P["candidate_episodes"]:
                agent.training=False
                scores=[deploy(agent,920000+j,sc)["total_cost"] for j,sc in enumerate(P["scenarios"])]
                candidates.append((statistics.mean(scores),i+1,freeze(agent)))
        val,ep,data=min(candidates,key=lambda c:(c[0],c[1]))
        agent.net.online.load_state_dict(torch.load(io.BytesIO(data),map_location="cpu",weights_only=True))
        assert all(torch.isfinite(x).all() for x in agent.net.online.state_dict().values())
        selection[seed]=dict(episode=ep,validation=[(e,v) for v,e,_ in candidates],
                             sha256=hashlib.sha256(data).hexdigest(),training_decisions=agent.steps)
        models[seed]=agent
        weights[str(seed)]=base64.b64encode(zlib.compress(data)).decode()
    (OUT/"models.json").write_text(json.dumps(weights))
    rows=[]
    for j,sc in enumerate(P["scenarios"]):
        for r in range(5):
            seed=930000+100*j+r
            events,loss=inputs(seed,sc)
            record=dict(scenario=sc,trace_seed=seed,trace_sha256=digest([events,loss]),results={})
            for policy in ["thesis","greedy"]:
                record["results"][policy]=run(policy,events,loss,write_logs=False)
            for m,agent in models.items():
                record["results"][str(m)]=run("adapted",events,loss,controller=agent,write_logs=False)
            assert len({v["offered"] for v in record["results"].values()})==1
            rows.append(record)
    (OUT/"results.json").write_text(json.dumps(dict(selection=selection,traces=rows),indent=1)+"\n")


if __name__=="__main__":
    main()
