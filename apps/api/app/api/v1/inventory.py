"""Inventory endpoints."""
from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import CurrentUser
from app.db.models import InventoryItem
from app.schemas import InventoryItemOut

router = APIRouter()


@router.get("", response_model=list[InventoryItemOut])
async def list_inventory(user: CurrentUser, request: Request):
    db = request.state.db
    items = (await db.execute(
        select(InventoryItem).where(InventoryItem.user_id == user.id).order_by(InventoryItem.acquired_at.desc())
    )).scalars().all()
    return [InventoryItemOut.model_validate(i) for i in items]
