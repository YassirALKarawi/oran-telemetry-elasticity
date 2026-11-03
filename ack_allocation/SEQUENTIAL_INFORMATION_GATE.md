# Sequential information/allocation: literature and formulation gate

Reviewed 3 November 2026. Preliminary targeted screening, not an exhaustive novelty search. No new training or network-performance experiment was run in this gate.

## Evidence actually inspected

| Primary source | Access inspected | Relevant overlap | What this inspection does not establish |
|---|---|---|---|
| Opportunistic admission and resource allocation for slicing enhanced IoT networks, DOI 10.1016/j.dcan.2022.08.007 | Publisher indexed text: introduction and model sections 2–3, including waiting cost and MDP. Direct page fetch returned 403; complete paper not verified. | Immediate versus deferred admission, heterogeneous resources, utility/resource/waiting costs and future decisions. | Whether its complete model handles delayed command acknowledgements or partial transaction outcomes. |
| Satsangi et al., Exploiting submodular value functions for scaling up active perception, Autonomous Robots 42, 209–233 (2018), DOI 10.1007/s10514-017-9666-5 | Open publisher full text, particularly sections 1–2 and model discussion. | Resource-constrained sensing and non-myopic POMDP planning; efficient planning is already an established research question. | Equivalence to SDN orchestration or transfer of its submodularity guarantees to admission utility. |
| Gholamipour et al., Online Admission Control and Resource Allocation in Network Slicing under Demand Uncertainties, arXiv:2108.03710v3 | Abstract/metadata only. | Joint communication/computation admission under uncertainty; robust optimization and scalable heuristic. | Full algorithm, reproducibility, or an ACK-specific gap. |

Sources:
- https://www.sciencedirect.com/science/article/pii/S2352864822001687
- https://doi.org/10.1016/j.dcan.2022.08.007
- https://link.springer.com/article/10.1007/s10514-017-9666-5
- https://arxiv.org/abs/2108.03710v3

The first source's admission deferral is motivated by future load/pricing, not demonstrated here as active information acquisition. The second concerns sensing/perception rather than this thesis's allocation objective. Their combination is a warning against a broad novelty claim, not proof that every specific protocol-aware formulation has already been solved.

## Candidate model: a conventional reference first

Use a finite-horizon partially observable Markov decision process (POMDP).
Hidden state includes physical link/CPU occupancy and individual command execution stages. Observable history contains delivered snapshots, source timestamps, command identifiers and received status messages. State belief b is conditioned only on that history.

Actions: allocate an admissible complete route, wait one epoch, request reconciliation if a documented interface supports it, or reject. Reconciliation and waiting consume time; reconciliation also has a communication/processing cost. Request deadlines and admission values are explicit. ACK silence is an observation governed by a delivery model, not proof of failure.

For horizon h, use the ordinary reference equation:

    V_h(b,q) = max_a [ r(b,q,a) + sum_o P(o|b,q,a) V_(h-1)(tau(b,q,a,o), q_next) ].

Here q includes observable pending requests and deadlines; tau is the Bayesian transition/observation update. Boundary rewards enforce expiration. Utility must measure completed feasible service minus costs, not entropy reduction alone. The interface/protocol must determine transitions and observable outcomes before parameters are fitted. This is a standard decision model, not a claimed novel algorithm.

## Why a simple demonstration would be insufficient

In a two-world migration example, one route is occupied in each world. Waiting for a reliable identifying status can enable safe route selection, whereas an immediate worst-case allocation may reject. This is a value-of-information effect expected from the POMDP reference. An adaptive method that beats static worst-case reservation merely because the latter cannot wait has unequal action sets; it is not evidence of algorithmic superiority.

No numbers are reported for that unexecuted illustration.

## Matched comparison and rejection conditions

1. Implement a small exact finite-horizon belief-state reference and a separately implemented policy-tree enumeration check. Both receive identical observation timing, uncertainty, costs, deadlines and actions.
2. Compare a scalable candidate against that reference where tractable; also compare an ordinary receding-horizon belief controller with the same actions. Include immediate robust allocation and fixed waiting as diagnostics only.
3. Report expected completed-service utility, missed deadlines, infeasible command attempts, signaling volume and planning time. Actual overload and rejected attempts remain separate.
4. Test zero observation delay, missing/lost/duplicate messages, timestamp reordering, uninformative probes, expensive probes and imminent deadlines. Policies must stop buying information when its cost outweighs downstream utility.
5. For stochastic network evaluation, predeclare independent seeds and paired workloads, parameter budgets, calibration data, training budget and confidence intervals. Hand-built examples are mechanism checks.
6. Reject a candidate whose gain disappears with matched information/actions, depends on future-message leakage, or is explained solely by ordinary belief-state planning.

## Unresolved evidence before a new contribution

- Retrieve complete closest network papers and extend the search to active sensing/control, deadline admission and transaction-aware orchestration.
- Select and inspect an actual SDN controller/adapter implementation. Document whether a returned status acknowledges receipt, installation or observed effect; do not assume these are interchangeable.
- Establish whether link and compute changes can partially commit, and how reconciliation observes that condition. Atomic application in the earlier toy simulator does not validate a real protocol.
- Obtain measured or justified command/observation delays and missing-message behavior. No deployment or protocol trace has been inspected in this gate.
- Identify a concrete structural result or scalable approximation with a defensible bound, or a measured system contribution. Neither has yet been established.

## Decision

Generic wait/probe/allocate control is not accepted as the thesis's new contribution at this stage. Preserve the completed PRORL baseline and the negative mechanism diagnostics. This gate does not imply that the thesis title must change or that publication is impossible. It prevents committing to a renamed conventional decision problem before protocol evidence and matched comparisons are available.
