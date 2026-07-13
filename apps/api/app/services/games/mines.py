"""Mines game helpers (board generation uses deterministic shuffle in engine)."""
def tiles_revealed(revealed: list[int], mine_positions: list[int]) -> tuple[bool, int]:
    """Check if a reveal hits a mine and count safe reveals.

    Returns (hit_mine, safe_count).
    """
    safe = 0
    for r in revealed:
        if r in mine_positions:
            return True, safe
        safe += 1
    return False, safe


def mines_multiplier(revealed: int, total_tiles: int, mines: int) -> float:
    """Pinnacle-style mines multiplier approximation."""
    if revealed == 0:
        return 1.0
    safe = total_tiles - mines
    mult = 1.0
    for i in range(revealed):
        mult *= total_tiles / (safe - i)
    # house edge
    return max(1.0, mult * 0.96)
