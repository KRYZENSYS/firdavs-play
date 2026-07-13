"""Auth endpoints: Telegram WebApp login + dev login fallback."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.core.security import (
    create_token,
    get_current_user,
    make_referral_code,
    validate_telegram_init_data,
)
from app.models import User, Referral

router = APIRouter()


class TelegramLoginRequest(BaseModel):
    init_data: str
    referral_code: str | None = None


class DevLoginRequest(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class AuthResponse(BaseModel):
    access_token: str
    user: dict


@router.post("/telegram", response_model=AuthResponse)
async def login_telegram(req: TelegramLoginRequest, db: AsyncSession = Depends(get_session)):
    user_data = None
    if settings.DEV_MODE and req.init_data.startswith("dev_"):
        # Dev shortcut
        try:
            tid = int(req.init_data.split("_", 1)[1])
            user_data = {"id": tid, "first_name": "Dev", "username": "dev"}
        except Exception:
            pass
    elif settings.BOT_TOKEN:
        user_data = validate_telegram_init_data(req.init_data)
    else:
        raise HTTPException(400, "Bot token not configured")

    if not user_data:
        raise HTTPException(401, "Invalid init data")

    tg_user = user_data.get("user", user_data)
    tg_id = int(tg_user["id"])

    res = await db.execute(select(User).where(User.telegram_id == tg_id))
    user = res.scalar_one_or_none()

    if not user:
        # Apply referral if provided and valid
        referred_by = None
        if req.referral_code:
            ref = await db.execute(select(User).where(User.referral_code == req.referral_code.upper()))
            ref_user = ref.scalar_one_or_none()
            if ref_user:
                referred_by = ref_user.telegram_id

        user = User(
            telegram_id=tg_id,
            username=tg_user.get("username"),
            first_name=tg_user.get("first_name") or "Player",
            last_name=tg_user.get("last_name"),
            photo_url=tg_user.get("photo_url"),
            language_code=tg_user.get("language_code"),
            is_premium=tg_user.get("is_premium", False),
            is_admin=(tg_id in settings.admin_ids),
            coins=1000,
            referral_code=make_referral_code(),
            referred_by=referred_by,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Credit referral bonus
        if user.referred_by and not user.is_banned:
            ref = await db.execute(select(User).where(User.telegram_id == user.referred_by))
            referrer = ref.scalar_one_or_none()
            if referrer and not referrer.is_banned:
                referrer.coins += settings.REFERRAL_BONUS
                db.add(Referral(referrer_id=referrer.id, referee_id=user.id, bonus_paid=True))
                user.coins += settings.REFERRAL_BONUS
                await db.commit()

    return AuthResponse(
        access_token=create_token(user.id, user.telegram_id),
        user=_user_to_dict(user),
    )


@router.post("/dev", response_model=AuthResponse)
async def login_dev(req: DevLoginRequest, db: AsyncSession = Depends(get_session)):
    """Dev-only login for local testing without Telegram."""
    if not settings.DEV_MODE:
        raise HTTPException(403, "Dev mode disabled")

    res = await db.execute(select(User).where(User.telegram_id == req.telegram_id))
    user = res.scalar_one_or_none()

    if not user:
        user = User(
            telegram_id=req.telegram_id,
            username=req.username,
            first_name=req.first_name or "Dev",
            coins=5000,
            is_admin=(req.telegram_id in settings.admin_ids),
            referral_code=make_referral_code(),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return AuthResponse(
        access_token=create_token(user.id, user.telegram_id),
        user=_user_to_dict(user),
    )


@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return _user_to_dict(user)


def _user_to_dict(u: User) -> dict:
    return {
        "id": u.id,
        "telegram_id": u.telegram_id,
        "username": u.username,
        "first_name": u.first_name,
        "last_name": u.last_name,
        "photo_url": u.photo_url,
        "language_code": u.language_code,
        "is_premium": u.is_premium,
        "is_admin": u.is_admin,
        "coins": u.coins,
        "xp": u.xp,
        "level": u.level,
        "games_played": u.games_played,
        "total_wagered": u.total_wagered,
        "total_won": u.total_won,
        "referral_code": u.referral_code,
        "daily_streak": u.daily_streak,
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }
