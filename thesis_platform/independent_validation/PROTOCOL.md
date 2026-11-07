# Independent frozen-policy transport validation

This protocol is locked before any test execution. It does not change the
`adaptive`, `thesis_floor`, or `proportional_floor` decision rules committed in
`382f530b8886ee2f049c6ebb2981b4a41c2ee471`. No threshold, floor, deadline,
offered load, seed, ordering, metric, or interpretation rule may be changed
after outcomes are available.

## Design

- Two independently allocated GitHub-hosted runner images execute the complete
  study: Ubuntu 22.04 and Ubuntu 24.04.
- The transport budget is 16 Mbit/s. Class deadlines are 15 and 40 ms. Every
  policy starts each trace at an equal 8/8 Mbit/s split and retains the frozen
  40% class-2 floor.
- Fast traces change the high-demand class every two-second window. Medium
  traces hold it for two windows. Slow traces hold it for four windows.
- Each speed has six fresh traces and all six policy-order permutations exactly
  once. Every trace contains eight windows. The explicit loads and seeds are in
  `independent_protocol.json`.
- The same trace is paired across policies within a host. Both hosts execute the
  exact same protocol. Host-image differences are reported as replication
  differences, not pooled as extra independent traffic traces.

## Locked endpoints

For each speed, host, and policy, report the equal-trace mean and sample standard
deviation of class-1 timely delivery, class-2 timely delivery, and combined timely
delivery. The denominator includes every sent packet. Retain timely, late, and
missing counts separately for each class.

Report these paired contrasts without a pass/fail claim: adaptive minus
`proportional_floor` for all three endpoints, and adaptive minus `thesis_floor`
for all three endpoints. Report positive, tied, and negative traces. Report the
same contrast differences between hosts. A host discrepancy greater than two
percentage points is flagged for investigation but does not invalidate or erase
either result.

The study is descriptive. It does not establish physical-radio performance,
state-of-the-art superiority, rare-event reliability, or long-run stability.
Negative contrasts and cross-host disagreements remain in the report.

## Evidence requirements

Each host must preserve the full per-window ledger, aggregate scores, decoded E2
request and acknowledgement list, packet capture, FlexRIC revision, build patch,
host metadata, and protocol hash. Verification recomputes metrics and the frozen
policy actions from the archives. A successful workflow status alone is
insufficient evidence.
