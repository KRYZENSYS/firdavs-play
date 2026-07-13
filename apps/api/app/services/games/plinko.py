"""Plinko: ball falls through rows of pegs, lands in a bin."""
PLINKO_MULTIPLIERS: dict[tuple[int, str], list[float]] = {
    (8, "low"):    [5.6, 2.1, 1.1, 1.0, 0.5, 1.0, 1.1, 2.1, 5.6],
    (8, "medium"): [13, 3, 1.3, 0.7, 0.4, 0.7, 1.3, 3, 13],
    (8, "high"):   [29, 4, 1.5, 0.3, 0.2, 0.3, 1.5, 4, 29],
    (12, "low"):   [10, 3, 1.6, 1.4, 1.1, 1.0, 0.5, 1.0, 1.1, 1.4, 1.6, 3, 10],
    (12, "medium"): [33, 11, 4, 2, 1.1, 0.6, 0.3, 0.6, 1.1, 2, 4, 11, 33],
    (12, "high"):  [170, 24, 8.1, 2, 0.7, 0.2, 0.2, 0.2, 0.7, 2, 8.1, 24, 170],
    (16, "low"):   [16, 9, 2, 1.4, 1.4, 1.2, 1.1, 1.0, 0.5, 1.0, 1.1, 1.2, 1.4, 1.4, 2, 9, 16],
    (16, "medium"): [110, 41, 10, 5, 3, 1.5, 1.0, 0.5, 0.3, 0.5, 1.0, 1.5, 3, 5, 10, 41, 110],
    (16, "high"):  [1000, 130, 26, 9, 4, 2, 0.2, 0.2, 0.2, 0.2, 0.2, 2, 4, 9, 26, 130, 1000],
}


def simulate(rows: int, rnd: float) -> int:
    """Random walk simulation returning the bin index."""
    pos = 0
    for _ in range(rows):
        # Each step: probability 0.5 of going right
        r = (rnd * 2 ** (_ + 1)) % 1
        if r > 0.5:
            pos += 1
    return pos


def multiplier(bin_x: int, rows: int, risk: str = "medium") -> float:
    key = (rows, risk)
    table = PLINKO_MULTIPLIERS.get(key)
    if not table:
        return 0.0
    bin_x = max(0, min(len(table) - 1, bin_x))
    return float(table[bin_x])
