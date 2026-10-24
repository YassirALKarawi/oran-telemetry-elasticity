Latest audit: see COLUMN_REVISION.md and reference_metadata_audit.json (24 October 2026). Earlier notes below are historical.

# Source audit for the current manuscript

Updated 23 October 2026. The current bibliography contains 43 distinct works.
The latest reconciliation in `JOURNAL_REVISION.md` supersedes the older
author-version status below for OREO and packet-level delay bounds, and
completes MAREA publication metadata. Journal selection and template provenance
are recorded there separately from research evidence.
It is a focused literature review, not an exhaustive systematic review. The
historical `SOURCE_AUDIT.md` describes the earlier thirteen-source report only.

## Added primary sources, checked 22 October 2026

- Kubernetes official Horizontal Pod Autoscaling documentation:
  https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/ .
  The implementation adapts target-based sizing and downscale stabilization.
  It does not reproduce Kubernetes replica metrics, tolerance or default timing.
- Neely's author version, *Energy-Aware Wireless Scheduling with Near Optimal
  Backlog and Convergence Time Tradeoffs*, https://arxiv.org/abs/1411.4740
  and https://arxiv.org/html/1411.4740v1 . Used for the cost-minus-queue-service
  principle only. No convergence or stability theorem is imported into the
  delayed deadline-normalized adaptation.
- Wang et al., *Delay-Tolerant Constrained OCO with Application to Network
  Resource Allocation*, https://arxiv.org/abs/2105.04005 and
  https://arxiv.org/html/2105.04005v1 . The author record identifies the INFOCOM
  DOI 10.1109/INFOCOM42981.2021.9488698. Used for formulation/guarantee positioning,
  not as an executed baseline.

The forty retained references below were audited in the preceding revision.
Their original access levels remain disclosed. This revision does not claim
to have reproduced forty-three full-text methods.

The reference dictionary preserves explicitly labelled author/preprint versions
where a final publisher record was not fully reconciled. An arXiv DOI is an
identifier for that author version, not an assertion of peer review. DOI links
and source links are blue in the manuscript. No journal quartile is inferred.

## Evidence levels and primary provenance

- Architecture, information age, OrchestRAN, OREO, CAORA, ColO-RAN, EdgeRIC,
  Colosseum and the three scheduler/network-calculus papers were checked using
  their author-provided arXiv abstract and metadata records. Their use is limited
  to problem scope and methodological distinctions, not detailed reproduction.
- MAREA and adaptive vBS allocation were inspected in author full-text sections
  on the respective allocation/learning formulations, alongside DOI metadata.
  See https://arxiv.org/html/2503.08599v2 and
  https://arxiv.org/html/2309.01730v2 .
- Demir et al.: https://arxiv.org/abs/2301.06166 .
- vrAIn: author-hosted paper,
  https://www.asaavedra.net/files/papers/2019_ayala_mobicom_vrain.pdf .
- Nuberu: author institution repository,
  https://dspace.networks.imdea.org/handle/20.500.12761/1566 .
- Concordia: author institution publication record and abstract,
  https://www.microsoft.com/en-us/research/publication/concordia-teaching-the-5g-vran-to-share-compute/ .
- O-RAN ecosystem: author publication page,
  https://www.asaavedra.net/publication/2021_garciasaavedra_magazine_oran/ .
- Murti et al.: https://arxiv.org/abs/2205.07518 .
- Wang et al.: publisher PDF and author institution repository,
  https://ieeexplore.ieee.org/iel7/6287639/10005208/10239168.pdf and
  https://dr.ntu.edu.sg/entities/publication/cda8f494-ae29-4645-9fae-0d908330bd07 .
- Kasuluru et al.: author project bibliography,
  https://free6g.cttc.es/index.php/publications . The journal volume year is
  **2026**, despite the DOI containing 2025.
- SORA and 5ERASI: author laboratory bibliography,
  https://www.nakao-lab.org/publications/journals/ . 5ERASI DOI also appears in
  the publisher PDF https://ieeexplore.ieee.org/iel8/6287639/6514899/11520643.pdf .
- COMIX: publisher PDF metadata,
  https://ieeexplore.ieee.org/iel8/6287639/10820123/11071295.pdf .
- RadioSaber: publisher abstract and full bibliographic record,
  https://www.usenix.org/conference/nsdi23/presentation/chen-yongzhou .
- OpenRAN Gym: https://arxiv.org/abs/2207.12362 , including publisher DOI.
- SCOPE: official author repository https://github.com/wineslab/colosseum-scope .
- FlexRIC: official implementation https://github.com/openaicellular/flexric .
- ns-O-RAN: https://arxiv.org/abs/2305.06906 , including conference DOI.
- 5G-LENA and calibration: official developer bibliography and calibration
  description, https://5g-lena.cttc.es/papers/ and
  https://5g-lena.cttc.es/features/calibration/ .
- SDN survey: author version https://arxiv.org/abs/1406.0440 and publisher page
  https://proceedingsoftheieee.ieee.org/software-defined-networking-a-comprehensive-survey/ .
- Networked control survey: author institution record
  https://www.ccdc.ucsb.edu/publications/11932 .
- Predictive control: publisher record
  https://www.sciencedirect.com/science/article/abs/pii/S0005109899002149 .
- Neely, deterministic network calculus and stochastic network calculus:
  publisher book records identified by the DOI links in `paper_references.py`.
  No theorem from these books is asserted to hold for the new heuristic.
- Sargent: publisher article record https://doi.org/10.1057/jos.2012.20 .
- Efron and Holm: publisher/archive metadata and stable identifiers, as documented
  in the historical source audit. Method attribution is not described as a
  full-text literature reproduction. Implementations are separately checked.

No external source supplies this simulator's numerical parameter values. Every
rate, deadline, capacity, delay, history length, margin and switching coefficient
is a disclosed synthetic choice. No performance number from another work is
treated as an experimentally reproduced baseline. No claim of a first-ever
forecasting, orchestration or fallback method is made.
# Publication-record refresh, 23 October 2026

Substantive rewrite check: MAREA's author full text at
https://arxiv.org/html/2503.08599v2 confirms the distinction between its
martingale-based delay treatment and the workload heuristic used here.
The TU Delft institutional publication record at
https://research.tudelft.nl/en/publications/adaptive-resource-allocation-for-virtualized-base-stations-in-o-r/
confirms Kalntis et al.'s final issue: IEEE Transactions on Communications,
73(3), 1787–1800, 2025. The bibliography now uses the final issue year rather
than the 2024 early-access year. These checks do not certify journal quartiles.

Four bibliography entries now cite journal versions. Metadata was checked against
the IEEE indexed publisher PDF for Polese et al. (10.1109/COMST.2023.3239220),
MIT DSpace publication record for Yates et al. (10.1109/JSAC.2021.3065072),
IEEE Computer Society record for ColO-RAN (10.1109/TMC.2022.3188013), and
IEICE publisher record for IWRR (10.1587/transcom.2021ITI0001).
Publisher access was metadata/snippet-level for the two IEEE records, not a
new full-text assessment. No journal quartile claim follows from these updates.

