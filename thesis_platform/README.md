# Thesis platform feasibility audit — 2 November 2026

Thesis title remains Optimal Resource Allocation in ORAN with SDN-Managed Orchestration. Three manuscripts are research targets, not established contributions or guaranteed acceptances.

## Verified preparation

The Orange ns-O-RAN-flexric repository was accessible by Git and its source checkout was initiated at commit 1398bb8d70791b8ee342da5101bc66fad01a6a86. Its documented FlexRIC revision is f56d4487507c7ace392f1ec3f598e7eeda670acc. The documented interface combination is E2AP v1.01 and KPM v3.00. These versions must not be mixed with FlexRIC defaults.

The environment has Python 3.12 and GCC 13, but lacks CMake, SWIG, bison, flex, pkg-config and SCTP development headers. System package installation failed because setgroups/setegid/seteuid operations are unavailable. No privileged escalation was attempted. A recursive source checkout additionally failed because e2sim-kpmv3 contains a nested nlohmann_json_release submodule without a URL mapping. The top-level E2 simulator revision is 732d64703bb7f4ba585c434a133cf4cf23972298. Source acquisition is not a successful build or platform run.

## What the inspected documentation actually supports

The example xApps control cell on/off, transmission power, and antenna ports. Documentation also provides a radio KPI catalogue. That does not establish runtime controls for SDN transport paths, link bandwidth or virtual CPU allocation. Those adapters and their observability must be implemented and tested explicitly. No end-to-end cross-domain controller has been run.

Sources: https://github.com/Orange-OpenSource/ns-O-RAN-flexric and https://openrangym.com/tutorials/ns-o-ran . The older ColO-RAN tutorial requires Docker for its RIC deployment. Docker is not automatically required for every FlexRIC command-line setup.

## Concrete platform acceptance test

1. Build pinned ns-3, E2 simulator and FlexRIC revisions on a Linux host with the documented dependencies and working SCTP.
2. Run one documented xApp. Preserve E2 registration, subscription, indication, control and observable-action logs.
3. Introduce a separately measurable transport bottleneck. Verify that a path/bandwidth change modifies packet-level delay and throughput as expected.
4. Add a documented processing-service model or a measured compute workload. Label simulated processing separately from real CPU provisioning. Verify its resource controls independently.
5. Instrument packet generation, completion, loss and queue occupancy with consistent clocks. Check offered = delivered + lost + outstanding at run completion.
6. Only then freeze the first paper's action space and competing methods. Success on an unrelated radio xApp is insufficient acceptance for cross-domain allocation.

## Three-paper research structure

Paper 1: identify and relieve radio/transport/processing bottlenecks at matched budget and offered load. A candidate mechanism is selecting the resource change with the greatest measured marginal service benefit. Its novelty must be checked before claiming it as a contribution.

Paper 2: extend a validated first model to stale observations and demand uncertainty, with an independently evaluated adaptive reserve. Require benefit against suitable robust alternatives, not only a fixed heuristic.

Paper 3: coordinate competing radio and transport/compute decisions, measuring stability and service outcomes. Require comparisons against existing coordination approaches. Do not split the same experiment into three publications.

Each manuscript requires its own research question, closest-work comparison, independent evidence and disclosed shared platform. Submission, acceptance and publication are different milestones. University requirements must be read from an official document before labeling any publication count a graduation requirement.

## Next required execution resource

A Linux host capable of installing the dependencies and running SCTP is needed to finish the platform acceptance test. The upstream recommends Ubuntu 22.04, at least 8 GB RAM and 20 GB free storage; these are platform prerequisites, not estimates of the resources needed for the full research campaign. No hardware purchase or paid service has been initiated.

Run `python preflight.py` to inspect another host before setup. The current outcome is blocked platform preparation, not completed experimental validation.
