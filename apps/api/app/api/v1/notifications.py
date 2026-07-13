"""Notifications endpoints."""
from fastapi import APIRouter
from sqlalchemy import select, update

from app.api.deps import CurrentUser
from app.db.models import Notification
from app.schemas import NotificationOut

router = APIRouter()


@router.get("", response_model=list[NotificationOut])
async def list_notifications(user: CurrentUser, request: Request, unread_only: bool = False):
    db = request.state.db
    q = select(Notification).where(Notification.user_id == user.id)
    if unread_only:
        q = q.where(Notification.read == False)
    rows = (await db.execute(q.order_by(Notification.created_at.desc()).limit(100))).scalars().all()
    return [NotificationOut.model_validate(n) for n in rows]


@router.post("/read-all")
async def mark_all_read(user: CurrentUser, request: Request):
    db = request.state.db
    await db.execute(
        update(Notification).where(Notification.user_id == user.id, Notification.read == False).values(read=True)
    )
    return {"ok": True}
