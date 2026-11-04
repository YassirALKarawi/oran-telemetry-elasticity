# Reward interpretation audit — 4 November 2026

Inspected baseline_prorl/prorl/environment/reward.py, class GapSurplusCostReward, at upstream revision 4c3c70c11e070e93c7077ce9f22f6ed9d9e178d2 with the recorded local compatibility changes, and the executed recovered_full.json environment.reward configuration.

The executed objective weights are [0.6, 0.3, 0.1] for normalized gap, negative surplus and negative action cost. They differ from the class constructor defaults [0.45, 0.45, 0.1]; manuscript equations must use the executed configuration. Training normalization is [0,10], evaluation normalization [0,1]. Training and evaluation reward magnitudes must not be plotted as if they had an identical scale.

For each non-pool node, the implementation subtracts demand from allocated resource, divides by resource-class capacity when gap_with_units is enabled, and floors the result. With executed delta_target=0, remaining gap is the negative sum of deficit magnitudes, while surplus sums positive floored deltas. Thus these are discretized allocation counters. Surplus is not directly a physical energy loss and a signed gap is not a delay measurement.

The scalarized reward combines normalized objectives. The displayed raw gap/surplus/cost totals alone are insufficient to reconstruct reward without normalization factors, null-step handling and aggregation rules. This audit inspected the scalarization call, not every helper or all tracker aggregation paths; those remain to be traced before an independent reward reconstruction is claimed.

For the completed seed10 model, low-demand evaluation yielded larger surplus and lower utility than Greedy. The implementation confirms that surplus is penalized in the objective. It does not establish why the learned policy retained that allocation; action-history and ablation evidence are required for a causal explanation. No reward or algorithm was changed after observing the stress-test results.

Manuscript wording suitable for integration: The evaluation objective assigns weights 0.6, 0.3 and 0.1 to normalized deficit, surplus and action-cost terms. These weights define a particular tradeoff and do not imply simultaneous optimization of each raw metric. Report the component metrics alongside utility, retain negative workload-shift results, and distinguish training normalization from evaluation normalization.

The seed20 trainer was observed active at 28,392 steps during this audit. Its incomplete outputs are excluded from final comparison tables. This audit advances numerical interpretation, not the unresolved novelty or physical-validation claims.
