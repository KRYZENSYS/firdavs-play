"""Leaderboard endpoints."""
from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import CurrentUser
from app.db.models import User
from app.schemas import LeaderboardEntry

router = APIRouter()


@router.get("/coins", response_model=list[LeaderboardEntry])
async def top_by_coins(request: Request, limit: int = 50):
    limit = max(1, min(100, limit))
    db = request.state.db
    users = (await db.execute(
        select(User).order_by(User.coins.desc()).limit(limit)
    )).scalars().all()
    return [
        LeaderboardEntry(
            user_id=u.id, username=u.username, first_name=u.first_name,
            photo_url=u.photo_url, coins=u.coins, level=u.level, xp=u.xp,
        )
        for u in users
    ]


@router.get("/xp", response_model=list[LeaderboardEntry])
async def top_by_xp(request: Request, limit: int = 50):
    limit = max(1, min(100, limit))
    db = request.state.db
    users = (await db.execute(
        select(User).order_by(User.xp.desc()).limit(limit)
    )).scalars().all()
    return [
        LeaderboardEntry(
            user_id=u.id, username=u.username, first_name=u.first_name,
            photo_url=u.photo_url, coins=u.coins, level=u.level, xp=u.xp,
        )
        for u in users
    ]


@router.get("/wagered", response_model=list[LeaderboardEntry])
async def top_by_wagered(request: Request, limit: int = 50):
    limit = max(1, min(100, limit))
    db = request.state.db
    users = (await db.execute(
        select(User).order_by(User.total_wagered.desc()).limit(limit)
    )).scalars().all()
    return [
        LeaderboardEntry(
            user_id=u.id, username=u.username, first_name=u.first_name,
            photo_url=u.photo_url, coins=u.coins, level=u.level, xp=u.xp,
        )
        for u in users
    ]
