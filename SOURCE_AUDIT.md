# Source and claim audit

Checked on 18 October 2026. The list is a focused source set, not an exhaustive
systematic review. Thirteen entries are included. The earlier requested target
of at least 40 relevant references for a journal manuscript is NOT yet met.
No placeholder DOI, invented author, or unverified journal quartile is inserted.
Preprint identifiers below identify author-provided versions and are not claims
of peer review. Accessing an abstract is not recorded as full-text review.

| No. | Source and stable locator | Evidence accessed | Permitted use |
|---|---|---|---|
| 1 | M. Polese, L. Bonati, S. D'Oro, S. Basagni, T. Melodia, Understanding O-RAN: Architecture, Interfaces, Algorithms, Security, and Research Challenges. arXiv:2202.01032v2, 2022. https://arxiv.org/abs/2202.01032 | Author abstract and metadata | Architectural motivation, not evidence that this code implements O-RAN |
| 2 | R. D. Yates, Y. Sun, D. R. Brown III, S. K. Kaul, E. Modiano, S. Ulukus, Age of Information: An Introduction and Survey. arXiv:2007.08564, 2020. https://arxiv.org/abs/2007.08564 | Author abstract and metadata | Timestamp-based information age and resource-limited updates |
| 3 | O. Adamuz-Hinojosa, L. Zanzi, V. Sciancalepore, X. Costa-Perez, MAREA: A Delay-Aware Multi-time-Scale Radio Resource Orchestrator for 6G O-RAN. IEEE Transactions on Communications, DOI:10.1109/TCOMM.2025.3552296. https://arxiv.org/html/2503.08599v2 | Author full text, especially radio-allocation and RT control sections, and DOI metadata | Martingale-based radio delay analysis and two-timescale control exist. Current heuristic does not reproduce those guarantees |
| 4 | M. Kalntis, G. Iosifidis, F. A. Kuipers, Adaptive Resource Allocation for Virtualized Base Stations in O-RAN With Online Learning. DOI:10.1109/TCOMM.2024.3461569. https://arxiv.org/html/2309.01730v2 | Author full text, learning formulation and meta-learner, and DOI metadata | Online-learning and trace-driven vBS resource allocation already exist. No head-to-head superiority claim here |
| 5 | O. T. Demir, M. Masoudi, E. Bjornson, C. Cavdar, Cell-Free Massive MIMO in O-RAN: Energy-Aware Joint Orchestration of Cloud, Fronthaul, and Radio Resources. IEEE JSAC 42(2), 356-372, 2024. DOI:10.1109/JSAC.2023.3336187. https://arxiv.org/abs/2301.06166 | Author abstract and publication metadata | Joint radio, fronthaul and cloud orchestration is not by itself a new contribution |
| 6 | F. Mungari, C. Puligheddu, A. Garcia-Saavedra, C. F. Chiasserini, OREO: O-RAN intElligence Orchestration of xApp-based network services. arXiv:2405.18198v2, 2024. https://arxiv.org/abs/2405.18198 | Author abstract and metadata | xApp sharing/orchestration with proof-of-concept tests is a different problem from this packet service chain |
| 7 | S. D. A. Shah, M. Hafeez, A. Salama, S. A. R. Zaidi, Proactive AI-and-RAN Workload Orchestration in O-RAN Architectures for 6G Networks. arXiv:2507.09124, 2025. https://arxiv.org/abs/2507.09124 | Author abstract and metadata | Predictive shared AI/RAN workload orchestration is existing prior art. Publication status not inferred |
| 8 | M. Polese, L. Bonati, S. D'Oro, S. Basagni, T. Melodia, ColO-RAN: Developing Machine Learning-based xApps for Open RAN Closed-loop Control on Programmable Experimental Platforms. arXiv:2112.09559v2, 2022. https://arxiv.org/abs/2112.09559 | Author abstract and metadata | Experimental O-RAN framework exists. Not executed or used for this study |
| 9 | N. Patriciello, S. Lagen, B. Bojovic, L. Giupponi, An E2E Simulator for 5G NR Networks. Simulation Modelling Practice and Theory 96, 101933, 2019. https://5g-lena.cttc.es/papers/ | Official developer bibliography and module overview | Candidate full-stack simulation environment, not a validation result for current code |
| 10 | K. Koutlia, B. Bojovic, Z. Ali, S. Lagen, Calibration of the 5G-LENA System Level Simulator in 3GPP reference scenarios. Simulation Modelling Practice and Theory 119, 102580, 2022. https://5g-lena.cttc.es/features/calibration/ | Official calibration description and developer bibliography | A documented external validation route. Its parameter values have not been imported into this synthetic model |
| 11 | B. Efron, Bootstrap Methods: Another Look at the Jackknife. The Annals of Statistics 7(1), 1-26, 1979. DOI:10.1214/aos/1176344552. https://doi.org/10.1214/aos/1176344552 | Publisher DOI resolves to matching article title, readable primary reprint metadata at https://doi.org/10.1007/978-1-4612-4380-9_41 | Bootstrap method attribution only. Full original text not inspected |
| 12 | S. Holm, A Simple Sequentially Rejective Multiple Test Procedure. Scandinavian Journal of Statistics 6, 65-70, 1979. https://www.jstor.org/stable/4615733 | Stable archive title confirmed, archive full text not readable in this session | Method attribution. Adjustment implementation additionally unit-tested |
| 13 | IEEE Communications Society, IEEE Transactions on Network and Service Management: scope and author information. https://www.comsoc.org/publications/journals/ieee-transactions-network-and-service-management | Official journal page | Scope includes theoretical and applied network/service-management research. No Q1 rank or acceptance guarantee inferred |

## Novelty conclusion

None of joint resource allocation, predictive control, O-RAN orchestration or
information-age prioritization is alone a defensible novelty claim. A possible
narrow contribution is the interaction between delayed telemetry, queued
actuation and paid capacity elasticity, but a complete closest-work comparison
and meaningful mathematical or empirical advance remain required. The current
finite-grid solution is exact only for its hand-defined per-decision surrogate.

## Parameter provenance

Every numeric simulation parameter, including slot length, traffic intensities,
deadlines, expansion limits, switching coefficient, history window and control
delays, is an explicit synthetic design choice. None is presented as taken from
the references above. The source set motivates interpretation and an external
validation route, not retrospective physical calibration.
