"""Audit logging helper."""
import json
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AuditLog


async def log_audit(
    db: AsyncSession,
    actor_id: int | None,
    action: str,
    target_user_id: int | None = None,
    metadata: dict | None = None,
    ip: str | None = None,
) -> None:
    entry = AuditLog(
        actor_id=actor_id,
        action=action,
        target_user_id=target_user_id,
        metadata_json=json.dumps(metadata, default=str) if metadata else None,
        ip=ip,
    )
    db.add(entry)
