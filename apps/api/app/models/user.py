from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Boolean, BigInteger, Float
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    language_code: Mapped[str | None] = mapped_column(String(8), nullable=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)

    coins: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    games_played: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_wagered: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_won: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    referral_code: Mapped[str] = mapped_column(String(16), unique=True, index=True, nullable=False)
    referred_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    last_daily_claim: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_weekly_claim: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    daily_streak: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_active: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
