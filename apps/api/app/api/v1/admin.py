"""Admin endpoints (require is_admin)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import require_admin
from app.models import User, GameBet, Notification, AuditLog, PromoCode

router = APIRouter()


@router.get("/stats")
async def stats(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_session),
):
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    banned = (await db.execute(select(func.count(User.id)).where(User.is_banned == True))).scalar() or 0  # noqa: E712
    total_bets = (await db.execute(select(func.count(GameBet.id)))).scalar() or 0
    total_wagered = (await db.execute(select(func.sum(GameBet.bet_amount)))).scalar() or 0
    total_payout = (await db.execute(select(func.sum(GameBet.payout)))).scalar() or 0
    return {
        "total_users": total_users,
        "banned_users": banned,
        "total_bets": total_bets,
        "total_wagered": total_wagered,
        "total_payout": total_payout,
        "house_profit": total_wagered - total_payout,
    }


@router.get("/users")
async def list_users(
    limit: int = 50,
    offset: int = 0,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_session),
):
    res = await db.execute(
        select(User).order_by(desc(User.id)).limit(min(limit, 200)).offset(offset)
    )
    users = res.scalars().all()
    return [
        {
            "id": u.id,
            "telegram_id": u.telegram_id,
            "username": u.username,
            "first_name": u.first_name,
            "coins": u.coins,
            "level": u.level,
            "is_banned": u.is_banned,
            "is_admin": u.is_admin,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


class CoinAdjust(BaseModel):
    user_id: int
    delta: int
    reason: str = ""


@router.post("/coins")
async def adjust_coins(
    req: CoinAdjust,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_session),
):
    res = await db.execute(select(User).where(User.id == req.user_id))
    target = res.scalar_one_or_none()
    if not target:
        raise HTTPException(404, "User not found")
    target.coins += req.delta
    db.add(AuditLog(
        actor_id=admin.id, action="adjust_coins",
        target=str(req.user_id),
        details={"delta": req.delta, "reason": req.reason},
    ))
    await db.commit()
    return {"ok": True, "new_balance": target.coins}


class BanRequest(BaseModel):
    user_id: int
    ban: bool
    reason: str = ""


@router.post("/ban")
async def ban_user(
    req: BanRequest,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_session),
):
    res = await db.execute(select(User).where(User.id == req.user_id))
    target = res.scalar_one_or_none()
    if not target:
        raise HTTPException(404, "User not found")
    target.is_banned = req.ban
    db.add(AuditLog(
        actor_id=admin.id,
        action="ban" if req.ban else "unban",
        target=str(req.user_id),
        details={"reason": req.reason},
    ))
    await db.commit()
    return {"ok": True, "is_banned": target.is_banned}


class PromoCreate(BaseModel):
    code: str
    reward_coins: int
    max_uses: int = 1


@router.post("/promo")
async def create_promo(
    req: PromoCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_session),
):
    code = req.code.strip().upper()
    res = await db.execute(select(PromoCode).where(PromoCode.code == code))
    if res.scalar_one_or_none():
        raise HTTPException(400, "Code already exists")
    pc = PromoCode(code=code, reward_coins=req.reward_coins, max_uses=req.max_uses)
    db.add(pc)
    await db.commit()
    return {"ok": True, "code": code}


@router.get("/logs")
async def list_logs(
    limit: int = 100,
    action: str | None = None,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_session),
):
    q = select(AuditLog).order_by(desc(AuditLog.id)).limit(min(limit, 500))
    if action:
        q = q.where(AuditLog.action == action)
    res = await db.execute(q)
    logs = res.scalars().all()
    return [
        {
            "id": l.id,
            "actor_id": l.actor_id,
            "action": l.action,
            "target": l.target,
            "details": l.details,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in logs
    ]


class Broadcast(BaseModel):
    title: str
    body: str
    type: str = "announcement"


@router.post("/broadcast")
async def broadcast(
    req: Broadcast,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_session),
):
    res = await db.execute(select(User.id))
    user_ids = [r[0] for r in res.all()]
    for uid in user_ids:
        db.add(Notification(
            user_id=uid, type=req.type, title=req.title, body=req.body,
        ))
    db.add(AuditLog(
        actor_id=admin.id, action="broadcast",
        details={"title": req.title, "recipients": len(user_ids)},
    ))
    await db.commit()
    return {"ok": True, "recipients": len(user_ids)}
