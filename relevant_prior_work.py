"""Position two verified, directly relevant prior publications."""
def integrate(t):
    changes=[
      ('These features\nmotivate accounting', r'''Energy-efficient server selection and load balancing have also been studied in virtualized O-RAN \cite{alkarawi2024}. These features
motivate accounting'''),
      ('The present study focuses on replaying already issued commands', r'''Energy-aware off-grid O-RAN optimization jointly adapts transmitter energy, processor speed and reconfigurable intelligent surface (RIS) phases under latency and energy constraints \cite{alkarawi2025}. Its resource decisions couple communication and computing, whereas the present model isolates delayed capacity activation and class-wise packet deadlines. The present study focuses on replaying already issued commands'''),
      ('Units are abstract resource cost units, not money, energy or measured power.', r'''Units are abstract resource cost units, not money, energy or measured power. Power-based O-RAN optimization requires an explicit physical consumption model, as in server-load balancing \cite{alkarawi2024} and joint radio/edge resource control \cite{alkarawi2025}. Accordingly, reductions in $J$ quantify provisioning-cost differences within the present service-chain model and do not establish energy savings.'''),
    ]
    for old,new in changes:
        assert old in t,old
        t=t.replace(old,new,1)
    return t
