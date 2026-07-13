"""Achievements endpoints."""
from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import CurrentUser
from app.db.models import Achievement, UserAchievement
from app.schemas import AchievementOut

router = APIRouter()


@router.get("", response_model=list[AchievementOut])
async def list_achievements(user: CurrentUser, request: Request):
    db = request.state.db
    achievements = (await db.execute(select(Achievement))).scalars().all()
    unlocked = (await db.execute(
        select(UserAchievement).where(UserAchievement.user_id == user.id)
    )).scalars().all()
    unlocked_map = {ua.achievement_id: ua for ua in unlocked}
    out = []
    for a in achievements:
        ua = unlocked_map.get(a.id)
        out.append(AchievementOut(
            id=a.id, code=a.code, title=a.title, description=a.description,
            icon=a.icon, reward_coins=a.reward_coins,
            unlocked_at=ua.unlocked_at if ua else None,
        ))
    return out
