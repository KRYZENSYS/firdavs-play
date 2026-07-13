"""Auth endpoints: Telegram WebApp initData, dev login."""
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select

from app.api.deps import CurrentUser
from app.core.config import settings
from app.core.security import create_access_token, validate_telegram_init_data
from app.db.models import User
from app.schemas import AuthResponse, UserOut
from app.services.audit import log_audit
from app.services.referral import apply_referral_bonus

router = APIRouter()


class TelegramAuthRequest(BaseModel):
    init_data: str
    referral_code: str | None = None


class DevLoginRequest(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str | None = "Player"


@router.post("/telegram", response_model=AuthResponse)
async def telegram_login(body: TelegramAuthRequest, request: Request):
    payload = validate_telegram_init_data(body.init_data)
    if not payload:
        if settings.APP_ENV == "development":
            payload = {"id": 1, "first_name": "Dev", "username": "dev_player"}
        else:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid Telegram signature")

    tg_id = int(payload.get("id"))
    db = request.state.db

    user = (await db.execute(select(User).where(User.telegram_id == tg_id))).scalar_one_or_none()
    if not user:
        user = User(
            telegram_id=tg_id,
            username=payload.get("username"),
            first_name=payload.get("first_name"),
            last_name=payload.get("last_name"),
            photo_url=payload.get("photo_url"),
            language_code=payload.get("language_code", "en"),
            coins=settings.DEFAULT_COINS,
            is_admin=tg_id in settings.admin_ids,
        )
        db.add(user)
        await db.flush()
        await log_audit(db, user.id, "user.register", ip=request.client.host if request.client else None)

    if body.referral_code:
        await apply_referral_bonus(db, user, body.referral_code)

    token = create_access_token(user.id, {"tg": user.telegram_id})
    return AuthResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/dev", response_model=AuthResponse)
async def dev_login(body: DevLoginRequest, request: Request):
    if settings.APP_ENV == "production":
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    db = request.state.db
    user = (await db.execute(select(User).where(User.telegram_id == body.telegram_id))).scalar_one_or_none()
    if not user:
        user = User(
            telegram_id=body.telegram_id,
            username=body.username,
            first_name=body.first_name,
            coins=settings.DEFAULT_COINS,
            is_admin=True,
        )
        db.add(user)
        await db.flush()
    token = create_access_token(user.id, {"tg": user.telegram_id})
    return AuthResponse(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
async def me(user: CurrentUser):
    return UserOut.model_validate(user)
