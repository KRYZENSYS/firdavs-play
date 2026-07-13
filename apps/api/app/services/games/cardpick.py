"""Card Pick (5 cards, pick 1, win if matches highest)."""
SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]


def shuffle(hash_hex: str, n: int = 5) -> list[dict]:
    cards = [{"rank": r, "suit": s, "value": RANKS.index(r) + 1} for s in SUITS for r in RANKS]
    out = []
    used = set()
    for i in range(n):
        chunk = hash_hex[i * 2 : (i + 1) * 2] or "00"
        idx = (int(chunk, 16) + i * 7) % 52
        while idx in used:
            idx = (idx + 1) % 52
        used.add(idx)
        out.append(cards[idx])
    return out


def match(chosen: int, cards: list[dict]) -> bool:
    if chosen < 0 or chosen >= len(cards):
        return False
    chosen_card = cards[chosen]
    return all(chosen_card["value"] >= c["value"] for c in cards)
