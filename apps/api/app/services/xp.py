"""XP and level helpers."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.services.games.engine import level_from_xp, xp_for_action


async def add_xp(db: AsyncSession, user: User, base_xp: int, action: str) -> None:
    multiplier = 1.0
    if user.is_premium:
        multiplier = 1.5
    user.xp += int(base_xp * multiplier)
    new_level = level_from_xp(user.xp)
    if new_level > user.level:
        user.level = new_level
