# Component evidence contract: executable diagnostic

3 November 2026. Run from repository root:

    python3 -m unittest discover -s ack_allocation/component_contract -p 'test_*.py' -v

This is a small proposed resource-accounting contract and eight deterministic
tests. It is not an OVS adapter, a network emulator, or protocol conformance
validation. A fresh executable lookup found no ovs-ofctl, ovs-vsctl,
ovs-vswitchd, Docker or Podman on the execution host. No live switch, container,
CPU provisioning or traffic experiment was launched.

Transport and compute reservations are tracked separately by command and
component ID. Unknown outcomes retain reservations. Positive application
evidence retains a reservation too. Failure in compute does not cancel a
successful transport change. A compensation request retains resources until
confirmed removal; failed compensation also retains them. Both required
components must have application evidence for configuration completion.
Configuration completion is deliberately not a packet-service/QoS measurement.

Evidence is an abstract trusted, authoritative adapter output. The adapter
must establish that not_applied means the allocation is absent, not merely
that a REST call failed. removed must identify the exact compensated allocation.
An OpenFlow barrier cannot be mapped to success without correlating errors.
These requirements remain unimplemented against a real protocol.

The assumed version is a strictly increasing authoritative component-evidence
revision for that operation and epoch. It is NOT an OpenFlow transaction ID,
wall-clock timestamp, or message delivery sequence. Stale/duplicate revisions
and foreign epochs are ignored. Reconnect requires explicit external
reconciliation; this small ledger has no automatic epoch migration. Unknown
command IDs fail rather than mutate unrelated entries. Command IDs must not
be reused. Reconciliation of authoritative newer evidence is permitted.

Scope limits: no allocator or capacity-admission check, no physical actuator,
no stochastic messages, no Byzantine evidence, no persistent ledger/restart,
no multi-switch transaction, and no measured latency or reliability. Component
amounts are abstract resource units. No novelty or performance gain is claimed.

Eight tests cover partial failure, timeout, pending/confirmed compensation,
failed compensation, stale/duplicate evidence, foreign epoch, duplicate issue,
and the requirement for both component confirmations. Tests verify these local
rules only. The isolated OVS acceptance experiment in SDN_SEMANTICS_AUDIT.md
remains blocked by the unavailable runtime. Do not replace atomic bundle
semantics with this cross-domain diagnostic.
