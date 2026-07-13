"""Referral system: tracking + bonus awards."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


REFERRAL_BONUS = 500


async def apply_referral_bonus(db: AsyncSession, user: User, code: str) -> None:
    """Apply referral if code is valid and not yet applied."""
    if user.referred_by:
        return  # already has referrer
    try:
        referrer_tg_id = int(code)
    except ValueError:
        return
    if referrer_tg_id == user.telegram_id:
        return
    referrer = (await db.execute(
        select(User).where(User.telegram_id == referrer_tg_id)
    )).scalar_one_or_none()
    if not referrer or referrer.is_banned:
        return
    user.referred_by = referrer.id
    user.coins += REFERRAL_BONUS
    referrer.coins += REFERRAL_BONUS
