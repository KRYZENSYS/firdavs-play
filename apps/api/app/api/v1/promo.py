"""Promo code endpoints."""
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select, insert

from app.api.deps import CurrentUser
from app.db.models import PromoCode, PromoRedemption
from app.schemas import PromoRedeemRequest, PromoRedeemResult
from app.services.audit import log_audit

router = APIRouter()


@router.post("/redeem", response_model=PromoRedeemResult)
async def redeem(body: PromoRedeemRequest, user: CurrentUser, request: Request):
    db = request.state.db
    code = (await db.execute(
        select(PromoCode).where(PromoCode.code == body.code.upper(), PromoCode.is_active == True)
    )).scalar_one_or_none()
    if not code:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invalid promo code")
    if code.expires_at and code.expires_at < datetime.utcnow():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Promo code expired")
    if code.used_count >= code.max_uses:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Promo code fully redeemed")

    existing = (await db.execute(
        select(PromoRedemption).where(PromoRedemption.user_id == user.id, PromoRedemption.promo_id == code.id)
    )).scalar_one_or_none()
    if existing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You already redeemed this code")

    await db.execute(insert(PromoRedemption).values(user_id=user.id, promo_id=code.id))
    code.used_count += 1
    user.coins += code.reward_coins
    await log_audit(db, user.id, "promo.redeem", metadata={"code": body.code, "reward": code.reward_coins})
    return PromoRedeemResult(success=True, coins_awarded=code.reward_coins, message="Promo code redeemed successfully")
