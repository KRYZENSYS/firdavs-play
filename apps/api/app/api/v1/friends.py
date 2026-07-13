"""Friends, gifts, chat endpoints."""
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select, insert

from app.api.deps import CurrentUser
from app.db.models import FriendRequest, Gift, User
from app.services.audit import log_audit

router = APIRouter()


class SendGiftRequest(BaseModel):
    to_user_id: int
    item_code: str
    amount: int = 1
    message: str | None = None


@router.post("/request/{to_user_id}")
async def send_friend_request(to_user_id: int, user: CurrentUser, request: Request):
    if to_user_id == user.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot friend yourself")
    db = request.state.db
    target = (await db.execute(select(User).where(User.id == to_user_id))).scalar_one_or_none()
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    try:
        await db.execute(insert(FriendRequest).values(from_user_id=user.id, to_user_id=to_user_id))
    except Exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Request already exists")
    return {"ok": True}


@router.post("/accept/{request_id}")
async def accept_friend_request(request_id: int, user: CurrentUser, request: Request):
    db = request.state.db
    fr = (await db.execute(
        select(FriendRequest).where(FriendRequest.id == request_id, FriendRequest.to_user_id == user.id)
    )).scalar_one_or_none()
    if not fr:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Request not found")
    fr.status = "accepted"
    return {"ok": True}


@router.post("/gift", response_model=dict)
async def send_gift(body: SendGiftRequest, user: CurrentUser, request: Request):
    if body.to_user_id == user.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot gift yourself")
    db = request.state.db
    await db.execute(insert(Gift).values(
        from_user_id=user.id, to_user_id=body.to_user_id,
        item_code=body.item_code, amount=body.amount, message=body.message,
    ))
    await log_audit(db, user.id, "gift.send", target_user_id=body.to_user_id, metadata={"item": body.item_code, "amount": body.amount})
    return {"ok": True, "message": "Gift sent"}
