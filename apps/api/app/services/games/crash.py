"""Crash game logic. Instant crash on round start; cashout at any time before crash."""
import math
import random
from typing import List


def crash_point(rnd: float) -> float:
    """Generate crash multiplier. House edge built-in via 1/(1-r) capped."""
    if rnd <= 0:
        return 1.0
    house_edge = 0.04
    raw = (1.0 - house_edge) / max(0.0001, 1.0 - rnd)
    return max(1.0, min(1000.0, math.floor(raw * 100) / 100))


def payout_multiplier(crash: float) -> float:
    return max(0.0, crash - 1.0)


def deterministic_shuffle(rng_list: List[float], n: int) -> List[float]:
    """Stable Fisher-Yates shuffle seeded by provided random floats."""
    arr = list(rng_list)[:n]
    for i in range(len(arr) - 1, 0, -1):
        j = int(arr[i] * (i + 1)) % (i + 1)
        arr[i], arr[j] = arr[j], arr[i]
    return arr
