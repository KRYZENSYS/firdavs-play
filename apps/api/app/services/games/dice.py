"""Dice helpers."""
def calculate_multiplier(target: float, over: bool) -> float:
    if over:
        return 100.0 / max(0.01, 100.0 - target)
    return 100.0 / max(0.01, target)
