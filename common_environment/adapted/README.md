# Paired evaluation of a PRORL-derived Double DQN controller

The protocol was committed at 14b069d22e3cb6046a414218ebf58f72f1bda846 before testing. This adaptation trains new policies for 304 joint capacity/share actions. It reuses upstream FullyConnected, TD estimate, online action selection for the bootstrap target, target-network evaluation, clipped optimizer update and synchronization. It substitutes tandem telemetry and the prespecified queue/capacity cost for the native state and reward. It uses uniform replay and omits the native expert and transfer-action decomposition. The original five bandwidth-allocation models remain a separate experiment.

Each independent training seed ran 18 episodes (1,296 decisions). At episodes 9 and 18 the mean validation cost over three traces determined selection. Each selected policy and both deterministic baselines then ran on the same 15 held-out input traces, five per scenario. All methods share the same delayed reports, feasible actions, service scheduling and command timing rules. Realized queue observations depend on prior actions. The cost penalizes cumulative queue backlog, active extra capacity and capacity changes; smaller values are preferable. Deadline misses count only arrivals whose deadline has elapsed by the horizon.

| Scenario | Controller | Cost | Extra unit-slots | Mean per-trace p99 (slots) | Misses / mature packets |
|---|---|---:|---:|---:|---:|
| nominal | Thesis | 117.90 | 21.0 | 4.40 | 0 / 4887 |
| nominal | Greedy | 154.13 | 196.0 | 4.80 | 0 / 4887 |
| nominal | Adapted DDQN | 324.42 | 1062.8 | 4.12 | 0 / 24435 |
| bursty_transport | Thesis | 563.08 | 757.0 | 21.00 | 0 / 6339 |
| bursty_transport | Greedy | 543.08 | 726.0 | 21.40 | 28 / 6339 |
| bursty_transport | Adapted DDQN | 790.48 | 1085.0 | 31.32 | 830 / 31695 |
| bursty_compute | Thesis | 626.19 | 697.0 | 23.80 | 0 / 6329 |
| bursty_compute | Greedy | 607.19 | 702.0 | 23.40 | 0 / 6329 |
| bursty_compute | Adapted DDQN | 1030.87 | 1116.6 | 40.84 | 2689 / 31645 |

The learned-policy denominators count repeated evaluations of the same packets under five checkpoints. The effective test set is five traffic traces per scenario. Nominal DDQN delay was smallest at much higher capacity cost. Under transport bursts, the thesis controller incurred greater cost than Greedy but had zero observed mature-packet misses. Under compute bursts, Greedy had lower mean cost and p99 than the thesis controller and both had zero misses. The short learning budget and synthetic trace family limit interpretation of the adapted agent's performance. These simulations provide no SDN/RIC deployment evidence.

From the repository root, use the pinned upstream checkout and patched environment described in prorl_reproduction/FIVE_SEED_PROTOCOL.json and environment.txt. Run `baseline_prorl/.venv/bin/python common_environment/adapted/replay.py` to reconstruct the paired test outcomes from the five saved weights. To rerun training, use train_adapted.py instead. models.json stores zlib-compressed, base64-encoded Torch state dictionaries and results.json contains each model digest, validation scores and all trace-level outcomes.
