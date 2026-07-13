"""Anti-cheat and rate limiting per-user for game actions."""
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import GameRound, User
from app.schemas import BetRequest
from app.services.redis_service import redis_service


async def validate_bet(db: AsyncSession, user: User, bet: BetRequest) -> None:
    """Per-user anti-cheat: max N bets per minute, max total wagered per day."""
    if not settings.ANTI_CHEAT_ENABLED:
        return

    # Per-minute cap (Redis-backed)
    key = f"anticheat:bet:{user.id}:{datetime.utcnow().strftime('%Y%m%d%H%M')}"
    try:
        count = await redis_service.incr(key, 1)
        if count == 1:
            await redis_service.expire(key, 70)
        if count > 30:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Too many bets per minute")
    except HTTPException:
        raise
    except Exception:
        pass  # fail-open if Redis is down

    # Daily wager cap
    daily_wagered = (await db.execute(
        select(func.coalesce(func.sum(GameRound.bet_amount), 0)).where(
            GameRound.user_id == user.id,
            GameRound.created_at > datetime.utcnow() - timedelta(days=1),
        )
    )).scalar() or 0

    max_daily = 1_000_000
    if daily_wagered + bet.bet_amount > max_daily:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Daily wager limit reached")

    # Suspicious win-rate check
    if user.games_played >= 50:
        win_rate = user.total_won / max(1, user.total_wagered)
        if win_rate > 5.0:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Suspicious activity detected")
