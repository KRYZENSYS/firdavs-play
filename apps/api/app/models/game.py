from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class GameBet(Base):
    """One bet on any game (instant or crash)."""
    __tablename__ = "game_bets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    game: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    round_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bet_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    payout: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    multiplier: Mapped[float] = mapped_column(Float, default=0.0)
    server_seed: Mapped[str] = mapped_column(String(64), nullable=False)
    client_seed: Mapped[str | None] = mapped_column(String(64), nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    won: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class CrashRound(Base):
    """Crash game round."""
    __tablename__ = "crash_rounds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    crash_point: Mapped[float] = mapped_column(Float, nullable=False)
    server_seed: Mapped[str] = mapped_column(String(64), nullable=False)
    hash: Mapped[str] = mapped_column(String(64), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="active")  # active | crashed


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    body: Mapped[str] = mapped_column(String(512), nullable=False)
    read: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_id: Mapped[int] = mapped_column(Integer, nullable=True)
    action: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    target: Mapped[str | None] = mapped_column(String(64), nullable=True)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    reward_coins: Mapped[int] = mapped_column(Integer, nullable=False)
    max_uses: Mapped[int] = mapped_column(Integer, default=1)
    used_count: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
