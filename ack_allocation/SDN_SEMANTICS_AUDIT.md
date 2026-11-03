# SDN command semantics audit

3 November 2026. Documentation and local source-scope audit; no switch experiment.

## Local evidence

Inspected thesis_platform/README.md, preflight_result.json and the Python/Markdown files in thesis_platform, joint_allocation and ack_allocation. The allocation models describe synthetic atomic resource changes, not an implemented SDN/CPU adapter. The broader nsoran_platform checkout includes upstream radio/E2 code; its presence is not a working transport/compute orchestrator. No ovs-ofctl or ovs-vsctl executable was found by command lookup on this host. No live switch connection, controller trace, CPU provisioning endpoint or cross-domain commit was tested.

The platform README records earlier missing build dependencies. That historical record is not a fresh dependency audit. Current executable absence blocks OVS command validation here; it does not prove that every possible external host is unavailable.

## Documented semantics

| Evidence | Meaning | Limit |
|---|---|---|
| OpenFlow 1.5.0 section 7.3.7 barrier reply | Earlier messages on the same connection have finished processing, with replies/errors sent, and resulting changes committed to the datapath under the specification's conditions. | Must correlate prior errors. Does not mean every command succeeded, or that CPU provisioning/end-to-end QoS succeeded. In-flight/queued packets have a stated exception. |
| OpenFlow section 6.3 channel rules | A barrier applies to its own connection. | It is not a transaction across switches or independent channels. |
| OVS flow modifications without --bundle | Earlier successful changes are not rolled back when a later modification fails. | Partial completion is possible for a sequence; not evidence of an observed fault rate. |
| OVS --bundle / supported OpenFlow bundles | Supported changes can form a single atomic transaction at one switch. | Do not invent partial application inside a successful atomic bundle; support and negotiated version must be checked. This does not cover a separate CPU API. |
| HTTP response from a future orchestration adapter | Meaning depends on that API's documented implementation. | A status code alone cannot be assigned generic received/applied/effect semantics. No such adapter implementation was verified here. |

OVS documentation also describes datapath cache revalidation behavior. Do not turn configuration visibility into a measured end-to-end latency guarantee. Version-specific behavior and conformance need a pinned implementation and traces.

Sources inspected:
- https://opennetworking.org/wp-content/uploads/2014/10/openflow-switch-v1.5.0.pdf — sections 6.2, 6.3, 7.3.7.
- https://docs.openvswitch.org/en/latest/topics/design/ — flow-table modification/atomicity discussion.
- https://www.openvswitch.org/support/dist-docs/ovs-ofctl.8.html — flow commands, bundle option.
Documentation pages are moving references, not pinned binary evidence.

## Required simulation correction for any successor

Keep the previous toy model as a disclosed atomic diagnostic. In a successor, represent transport and processing as separate components. Each has issued, unknown, confirmed-applied or confirmed-failed status, accompanied by command ID, component ID, connection/session epoch and evidence timestamp. Unknown includes timeout. Neither timeout nor failure in one component cancels a successful reservation in another.

A paired operation may therefore be transport-only, processing-only, both, neither, or unknown to the controller. Only matching component evidence changes that belief. Compensation is another fallible command; issuing rollback does not establish rollback completion. Observed service effect must be logged separately from configuration evidence.

This is a proposed adapter contract. It is not an implemented state machine or a novel protocol.

## Acceptance experiment before algorithm claims

On an isolated, pinned OVS environment:
1. Record versions, negotiated OpenFlow capabilities and initial flow state.
2. Compare a non-bundled sequence containing an invalid operation with the same supported operations in an atomic bundle; retain errors and read-back state.
3. Correlate transaction IDs and same-connection barriers; test disconnect/reconnect without interpreting silence as failure.
4. Add an independently observed processing control and inject a failure between component commits. Log reconciliation and compensation.
5. Measure packet service separately, retaining offered/delivered/lost/outstanding counts and synchronized timestamps.

No existing network should be modified by this procedure. Use an isolated test bridge/host. No experiment results, failure probabilities, latency values or novelty claims are available from this audit.

## Decision

There is a defensible modeling distinction between single-switch atomic updates and separate-domain orchestration. It is a systems requirement to investigate, not demonstrated scientific novelty. The next executable prerequisite is a functioning isolated SDN plus compute adapter with correlated traces. Until then, large training on invented cross-domain ACK semantics is not justified. Completed PRORL artifacts remain available and unchanged.
