"""User endpoints: profile, stats, game history, daily bonus."""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select

from app.api.deps import CurrentUser
from app.core.config import settings
from app.db.models import GameRound
from app.schemas import DailyBonusResult, GameRoundOut, UserOut, UserUpdate
from app.services.audit import log_audit
from app.services.daily_bonus import claim_daily, claim_weekly
from app.services.xp import add_xp

router = APIRouter()


@router.get("/me", response_model=UserOut)
async def get_me(user: CurrentUser):
    return UserOut.model_validate(user)


@router.patch("/me", response_model=UserOut)
async def update_me(body: UserUpdate, user: CurrentUser, request: Request):
    if body.language_code:
        user.language_code = body.language_code
    await request.state.db.flush()
    return UserOut.model_validate(user)


@router.post("/daily-bonus", response_model=DailyBonusResult)
async def daily_bonus(user: CurrentUser, request: Request):
    result = await claim_daily(request.state.db, user)
    if not result.claimed:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Daily bonus already claimed")
    await add_xp(request.state.db, user, settings.DAILY_BONUS, "daily_bonus")
    await log_audit(request.state.db, user.id, "bonus.daily", ip=request.client.host if request.client else None, metadata={"coins": result.coins_awarded})
    return result


@router.post("/weekly-bonus", response_model=DailyBonusResult)
async def weekly_bonus(user: CurrentUser, request: Request):
    result = await claim_weekly(request.state.db, user)
    if not result.claimed:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Weekly bonus already claimed")
    await add_xp(request.state.db, user, settings.WEEKLY_BONUS, "mission")
    return result


@router.get("/history", response_model=list[GameRoundOut])
async def history(user: CurrentUser, request: Request, limit: int = 50):
    limit = max(1, min(200, limit))
    rows = (await request.state.db.execute(
        select(GameRound).where(GameRound.user_id == user.id).order_by(GameRound.created_at.desc()).limit(limit)
    )).scalars().all()
    return [GameRoundOut.model_validate(r) for r in rows]
