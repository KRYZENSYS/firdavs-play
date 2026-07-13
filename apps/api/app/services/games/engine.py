"""Game engine: server-side validation, RNG, and provably fair outcomes.

All game outcomes are generated server-side using cryptographic RNG combined
with a provably fair scheme (server_seed + client_seed + nonce).
"""
from __future__ import annotations

import hashlib
import hmac
import math
import secrets
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.core.config import settings


def new_server_seed() -> str:
    return secrets.token_hex(32)


def outcome_hash(server_seed: str, client_seed: str, nonce: int) -> str:
    return hmac.new(
        server_seed.encode(),
        f"{client_seed}:{nonce}".encode(),
        hashlib.sha256,
    ).hexdigest()


def hash_to_float(hex_str: str, offset: int = 0) -> float:
    """Map 8 hex chars starting at `offset` to a float in [0, 1)."""
    chunk = hex_str[offset * 8 : offset * 8 + 8]
    if len(chunk) < 8:
        chunk = (chunk + "0" * 8)[:8]
    n = int(chunk, 16)
    return n / 0xFFFFFFFF


@dataclass
class GameResult:
    outcome: str
    multiplier: float
    payout: int
    payload: dict | None


def apply_house_edge(multiplier: float) -> float:
    """Apply house edge so that RTP = 1 - HOUSE_EDGE."""
    return multiplier * (1 - settings.HOUSE_EDGE)


def place_bet(
    *,
    game: str,
    bet_amount: int,
    server_seed: str,
    client_seed: str,
    nonce: int,
    bet_data: dict | None = None,
) -> GameResult:
    """Run a game round. Returns GameResult with multiplier/payout/outcome."""
    if bet_amount < settings.MIN_BET or bet_amount > settings.MAX_BET:
        raise ValueError(f"Bet must be between {settings.MIN_BET} and {settings.MAX_BET}")

    from app.services.games import crash, mines, plinko, dice, coinflip, wheel, cardpick, keno, limbo, hilo, towers

    h = outcome_hash(server_seed, client_seed, nonce)
    rnd = hash_to_float(h, 0)
    payload: dict | None = None

    if game == "crash":
        crash_point = crash.crash_point(rnd)
        mult = crash.payout_multiplier(crash_point)
        return GameResult(outcome=f"crash@{crash_point:.2f}x", multiplier=mult, payout=0, payload={"crash_point": crash_point})

    if game == "mines":
        size = int((bet_data or {}).get("size", 5))
        mines_count = int((bet_data or {}).get("mines", 3))
        mines_count = max(1, min(20, mines_count))
        size = max(2, min(8, size))
        rnd_grid = [hash_to_float(h, i + 1) for i in range(64)]
        rng_grid = crash.deterministic_shuffle(rnd_grid, size * size)
        placed = []
        for i in range(mines_count):
            placed.append(rng_grid[i] < 0.5)
        return GameResult(
            outcome="pending",
            multiplier=0.0,
            payout=0,
            payload={"size": size, "mines": mines_count, "seed_grid": rng_grid[: size * size]},
        )

    if game == "plinko":
        rows = int((bet_data or {}).get("rows", 12))
        rows = max(8, min(16, rows))
        risk = (bet_data or {}).get("risk", "medium")
        bin_x = plinko.simulate(rows, rnd)
        mult = plinko.multiplier(bin_x, rows, risk)
        mult = apply_house_edge(mult)
        payout = int(bet_amount * mult)
        return GameResult(outcome=f"bin_{bin_x}", multiplier=mult, payout=payout, payload={"bin": bin_x, "rows": rows, "risk": risk})

    if game == "dice":
        target = float((bet_data or {}).get("target", 50.0))
        over = bool((bet_data or {}).get("over", True))
        target = max(1.0, min(98.0, target))
        roll = rnd * 100
        won = (over and roll > target) or (not over and roll < target)
        if won:
            mult = (100 / (100 - target)) if over else (100 / target)
        else:
            mult = 0
        mult = apply_house_edge(mult)
        payout = int(bet_amount * mult) if won else 0
        return GameResult(outcome=("win" if won else "lose"), multiplier=mult, payout=payout, payload={"roll": round(roll, 2), "target": target, "over": over})

    if game == "coinflip":
        side = (bet_data or {}).get("side", "heads")
        result = "heads" if rnd < 0.5 else "tails"
        won = result == side
        mult = apply_house_edge(1.95)
        payout = int(bet_amount * mult) if won else 0
        return GameResult(outcome=result, multiplier=mult if won else 0, payout=payout, payload={"side": side, "won": won})

    if game == "wheel":
        idx = int(rnd * len(wheel.SEGMENTS))
        idx = min(idx, len(wheel.SEGMENTS) - 1)
        seg = wheel.SEGMENTS[idx]
        mult = apply_house_edge(seg["mult"])
        payout = int(bet_amount * mult)
        return GameResult(outcome=seg["label"], multiplier=mult, payout=payout, payload={"segment": idx, "color": seg["color"]})

    if game == "cardpick":
        chosen = int((bet_data or {}).get("card_index", 0))
        chosen = max(0, min(4, chosen))
        cards = cardpick.shuffle(h, 5)
        won = cardpick.match(chosen, cards)
        mult = apply_house_edge(4.0) if won else 0
        payout = int(bet_amount * mult) if won else 0
        return GameResult(outcome=("win" if won else "lose"), multiplier=mult, payout=payout, payload={"chosen": chosen, "cards": cards})

    if game == "keno":
        picks = (bet_data or {}).get("picks", [1, 2, 3, 4, 5])
        hits = (bet_data or {}).get("hits", 10)
        drawn = keno.draw(h, 10)
        matches = keno.matches(picks, drawn)
        mult = apply_house_edge(keno.multiplier(len(picks), matches))
        payout = int(bet_amount * mult)
        return GameResult(outcome=f"matches_{matches}", multiplier=mult, payout=payout, payload={"drawn": drawn, "picks": picks, "matches": matches})

    if game == "limbo":
        target = float((bet_data or {}).get("target", 2.0))
        target = max(1.01, min(1000.0, target))
        # House edge: probability of success = (1 - edge) / target
        threshold = (1 - settings.HOUSE_EDGE) / target
        won = rnd < threshold
        mult = apply_house_edge(target) if won else 0
        payout = int(bet_amount * mult) if won else 0
        return GameResult(outcome=("win" if won else "lose"), multiplier=mult, payout=payout, payload={"target": target, "roll": round(rnd, 6)})

    if game == "hilo":
        guess = (bet_data or {}).get("guess", "higher")
        current = int((bet_data or {}).get("current", 7))
        next_card = int(hash_to_float(h, 1) * 13) + 1
        next_card = max(1, min(13, next_card))
        won = (guess == "higher" and next_card > current) or (guess == "lower" and next_card < current)
        mult = apply_house_edge(1.95) if won else 0
        payout = int(bet_amount * mult) if won else 0
        return GameResult(outcome=("win" if won else "lose"), multiplier=mult, payout=payout, payload={"current": current, "next": next_card, "guess": guess})

    if game == "towers":
        rows = int((bet_data or {}).get("rows", 8))
        rows = max(3, min(10, rows))
        difficulty = (bet_data or {}).get("difficulty", "medium")
        bombs_per_row = {"easy": 1, "medium": 2, "hard": 3}.get(difficulty, 2)
        grid = towers.generate(h, rows, 4, bombs_per_row)
        return GameResult(outcome="pending", multiplier=0, payout=0, payload={"rows": rows, "difficulty": difficulty, "grid": grid})

    raise ValueError(f"Unknown game: {game}")


def level_from_xp(xp: int) -> int:
    """Level curve: level n requires n*100 cumulative XP."""
    if xp <= 0:
        return 1
    # Solve n(n+1)/2 * 100 = xp → n = (sqrt(1 + 8*xp/100) - 1) / 2
    n = (math.sqrt(1 + 8 * xp / 100) - 1) / 2
    return max(1, int(n) + 1)


def xp_for_action(action: str) -> int:
    return {
        "bet": 5,
        "win": 15,
        "daily_bonus": 25,
        "mission": 50,
        "achievement": 100,
    }.get(action, 1)
