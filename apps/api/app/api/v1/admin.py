"""Admin endpoints: user mgmt, coin mgmt, stats, promo creation, logs."""
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select, insert, update, func

from app.api.deps import AdminUser
from app.db.models import User, PromoCode, AuditLog, GameRound, Notification
from app.services.audit import log_audit

router = APIRouter()


class CoinUpdateRequest(BaseModel):
    user_id: int
    delta: int
    reason: str


class BanRequest(BaseModel):
    user_id: int
    ban: bool
    reason: str | None = None


class PromoCreateRequest(BaseModel):
    code: str
    reward_coins: int
    max_uses: int = 1
    expires_at: datetime | None = None


class BroadcastRequest(BaseModel):
    type: str = "system"
    title: str
    body: str


@router.get("/stats")
async def stats(_: AdminUser, request: Request):
    db = request.state.db
    user_count = (await db.execute(select(func.count(User.id)))).scalar() or 0
    total_coins = (await db.execute(select(func.coalesce(func.sum(User.coins), 0)))).scalar() or 0
    total_wagered = (await db.execute(select(func.coalesce(func.sum(User.total_wagered), 0)))).scalar() or 0
    rounds_today = (await db.execute(
        select(func.count(GameRound.id)).where(GameRound.created_at > datetime.utcnow() - timedelta(days=1))
    )).scalar() or 0
    return {
        "users": user_count, "total_coins": total_coins,
        "total_wagered": total_wagered, "rounds_today": rounds_today,
    }


@router.get("/users")
async def list_users(_: AdminUser, request: Request, limit: int = 50, offset: int = 0):
    db = request.state.db
    limit = max(1, min(200, limit))
    offset = max(0, offset)
    users = (await db.execute(
        select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
    )).scalars().all()
    return [
        {
            "id": u.id, "telegram_id": u.telegram_id, "username": u.username,
            "first_name": u.first_name, "coins": u.coins, "level": u.level,
            "is_admin": u.is_admin, "is_banned": u.is_banned, "is_premium": u.is_premium,
            "games_played": u.games_played, "total_wagered": u.total_wagered,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


@router.post("/coins")
async def adjust_coins(body: CoinUpdateRequest, _: AdminUser, request: Request):
    db = request.state.db
    user = (await db.execute(select(User).where(User.id == body.user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    user.coins = max(0, user.coins + body.delta)
    await log_audit(db, user.id, "admin.coins", target_user_id=user.id, metadata={"delta": body.delta, "reason": body.reason})
    return {"ok": True, "new_balance": user.coins}


@router.post("/ban")
async def ban_user(body: BanRequest, _: AdminUser, request: Request):
    db = request.state.db
    user = (await db.execute(select(User).where(User.id == body.user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    user.is_banned = body.ban
    await log_audit(db, user.id, "admin.ban", target_user_id=user.id, metadata={"banned": body.ban, "reason": body.reason})
    return {"ok": True, "is_banned": user.is_banned}


@router.post("/promo")
async def create_promo(body: PromoCreateRequest, _: AdminUser, request: Request):
    db = request.state.db
    code = body.code.upper()
    existing = (await db.execute(select(PromoCode).where(PromoCode.code == code))).scalar_one_or_none()
    if existing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Code already exists")
    await db.execute(insert(PromoCode).values(
        code=code, reward_coins=body.reward_coins,
        max_uses=body.max_uses, expires_at=body.expires_at, is_active=True,
    ))
    return {"ok": True, "code": code}


@router.get("/logs")
async def list_logs(_: AdminUser, request: Request, limit: int = 100, action: str | None = None):
    db = request.state.db
    limit = max(1, min(500, limit))
    q = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    if action:
        q = q.where(AuditLog.action == action)
    rows = (await db.execute(q)).scalars().all()
    return [
        {
            "id": l.id, "actor_id": l.actor_id, "action": l.action,
            "target_user_id": l.target_user_id, "ip": l.ip,
            "metadata": l.metadata_json, "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in rows
    ]


@router.post("/broadcast")
async def broadcast(body: BroadcastRequest, _: AdminUser, request: Request):
    db = request.state.db
    user_ids = (await db.execute(select(User.id))).scalars().all()
    for uid in user_ids:
        await db.execute(insert(Notification).values(
            user_id=uid, type=body.type, title=body.title, body=body.body,
        ))
    return {"ok": True, "delivered": len(user_ids)}
