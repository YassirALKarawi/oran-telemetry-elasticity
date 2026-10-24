# Journal revision — 23 October 2026

Target: IEEE Open Journal of the Communications Society (OJ-COMS).
The scope includes network control, QoS, reliability and distributed resource
control. The IEEE January 2026 title list reports Q1 (JIF), JIF 6.1 and ESCI
indexing for this title. This is a dated classification, not a guarantee of
acceptance or a claim that every cited journal is Q1.

- Official guidelines: https://www.comsoc.org/publications/journals/ieee-ojcoms/policies-guidelines
- Classification: https://open.ieee.org/wp-content/uploads/IEEE-Title-List-January-2026.pdf
- Author templates: https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/tools-for-ieee-authors/ieee-article-templates/

The manuscript uses IEEE's `IEEEoj.cls`, whose internal header identifies
IEEE Open Journals v1.0, 2020-06-19. The class itself is unmodified. Direct
access to IEEE's template selector was blocked during this preparation, so
the class was recovered from the author-deposited arXiv source package
https://arxiv.org/src/2509.06781 (version available on the access date).
This is the common IEEE Open Journals class required by the target journal,
not a claim to have downloaded the newest OJ-COMS-specific ZIP. Submission
metadata, logo placeholder and author marks are handled in the manuscript
preamble. There is no invented DOI, acceptance date, volume or publication
license. A text journal heading replaces the logo placeholder. The two wide
audit tables use single-column appendix pages for readability.

## Changes

- Study-level comparison table, with numeric citations and explicit limits.
- Continuous results section, without subsections, connecting uncertainty,
  command timing, headroom, integer reservations and observed failures.
- Structural deadline slack, irrecoverable cohort count and a necessary
  miss-fraction bound derived from the existing packet event order.
- Verification of the bound during six independent unchanged packet replays.
- New symbols included in the notation table and explained at first use.
- Top rule above both algorithm titles. All original pseudocode remains
  byte-identical after removing the explicitly added rule.
- IEEE Open Journals typography, wrapped two-column equations, author order
  and Hamed Al-Raweshidy as corresponding author.
- Standalone vector architecture and timeline files in `submission_figures`.
  The architecture is also supplied as `Graphical_Abstract.pdf`, an allowed
  figure-based graphical abstract under the journal's guidance.

## Reference reconciliation

The bibliography remains 43 distinct works. Original derivations are labelled
as such instead of being falsely attributed to references. Older foundational
sources are retained where they are the source of a method.

- OREO upgraded to the 2025 IEEE TMC journal extension,
  DOI https://doi.org/10.1109/TMC.2025.3527707 . Institutional full text:
  https://iris.polito.it/retrieve/handle/11583/2996162/cdae9be2-3e29-46d0-b0da-514aba8c8627/OREO-2.pdf
- MAREA publisher metadata reconciled to 73(9), 7695–7710 (2025):
  https://ieeexplore.ieee.org/document/10930661/ . Modeling distinctions
  checked in https://arxiv.org/html/2503.08599v2 .
- Packet-delay bounds upgraded to the published title and 2023 IEEE/ACM ToN
  record: https://ieeexplore.ieee.org/document/10144341/ ,
  DOI https://doi.org/10.1109/TNET.2023.3275910 .
- The 2026 multivariate forecasting paper was checked in the author project's
  published PDF: https://unity-6g.eu/wp-content/uploads/2026/02/Cloud-Native_Multivariate_Probabilistic_Forecasting_for_Next-Generation_Resource_Allocation_in_O-RAN.pdf
- Adaptive vBS allocation was checked in the institutional published copy:
  https://pure.tudelft.nl/ws/portalfiles/portal/241435950/Adaptive_Resource_Allocation_for_Virtualized_Base_Stations_in_O-RAN_With_Online_Learning.pdf

## Evidence boundary

All 336 calibration and 840 held-out execution records are unchanged. No new
performance observations or deployment results have been invented. The
independent checks verify the expanded mathematics against the existing
execution semantics. They do not establish physical O-RAN validity, rare-event
reliability, or superiority over unreproduced state-of-the-art implementations.
Author biographies, ORCIDs, funding declarations and publication consent have
not been fabricated. They remain author-supplied submission information.
