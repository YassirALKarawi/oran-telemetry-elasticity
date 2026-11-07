def choose(method, thesis, sent, received):
    """Return class-1 units for the next window using only completed observations."""
    n = sum(sent)
    proportional = (40*sent[0] + n) // (2*n)
    baseline = max(1, min(12, proportional))
    guarded = max(1, min(12, thesis))
    if method == "proportional_floor":
        return baseline
    if method == "adaptive":
        if sent[1] > 0 and 100*(sent[1] - received[1]) >= 5*sent[1]:
            return min(guarded, baseline)
        return guarded
    if method == "thesis_floor":
        return guarded
    raise ValueError(method)
