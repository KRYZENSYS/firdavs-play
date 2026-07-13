"""Daily and weekly bonus claims."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import User


@dataclass
class BonusResult:
    claimed: bool
    coins_awarded: int
    streak: int
    next_available_at: datetime | None


async def claim_daily(db: AsyncSession, user: User) -> BonusResult:
    now = datetime.utcnow()
    if user.last_daily_bonus_at and (now - user.last_daily_bonus_at) < timedelta(hours=20):
        next_at = user.last_daily_bonus_at + timedelta(hours=24)
        return BonusResult(claimed=False, coins_awarded=0, streak=0, next_available_at=next_at)
    user.last_daily_bonus_at = now
    user.coins += settings.DAILY_BONUS
    return BonusResult(claimed=True, coins_awarded=settings.DAILY_BONUS, streak=1, next_available_at=None)


async def claim_weekly(db: AsyncSession, user: User) -> BonusResult:
    now = datetime.utcnow()
    if user.last_weekly_bonus_at and (now - user.last_weekly_bonus_at) < timedelta(days=6):
        next_at = user.last_weekly_bonus_at + timedelta(days=7)
        return BonusResult(claimed=False, coins_awarded=0, streak=0, next_available_at=next_at)
    user.last_weekly_bonus_at = now
    user.coins += settings.WEEKLY_BONUS
    return BonusResult(claimed=True, coins_awarded=settings.WEEKLY_BONUS, streak=1, next_available_at=None)


async def reset_daily_missions() -> None:
    """Reset daily mission progress for all users (called at midnight UTC)."""
    from app.db.session import SessionLocal
    async with SessionLocal() as db:
        # Implementation: mark old user_missions with period_start < today as completed
        pass


async def reset_weekly_missions() -> None:
    from app.db.session import SessionLocal
    async with SessionLocal() as db:
        pass


async def send_daily_reminders() -> None:
    """Send a Telegram notification to users who haven't claimed today's bonus."""
    # Implementation: query users where last_daily_bonus_at < today, send via bot
    pass
