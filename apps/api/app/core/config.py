from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Server
    PORT: int = 3000
    HOST: str = "0.0.0.0"

    # Database — SQLite for Replit, Postgres for production
    DATABASE_URL: str = "sqlite+aiosqlite:///./firdavs.db"

    # Auth
    JWT_SECRET: str = "change-me-in-production-please-use-a-very-long-secret-key-here"
    JWT_ALG: str = "HS256"
    JWT_TTL_HOURS: int = 24 * 30  # 30 days

    # Telegram bot
    BOT_TOKEN: str = ""
    BOT_USERNAME: str = "FirdavsPlayBot"
    ADMIN_TELEGRAM_IDS: str = ""  # comma-separated
    WEBAPP_URL: str = "http://localhost:3000"

    # Game tuning
    HOUSE_EDGE: float = 0.04  # 4%
    DAILY_BONUS: int = 100
    WEEKLY_BONUS: int = 1000
    REFERRAL_BONUS: int = 500

    # Demo / dev mode (no real Telegram initData validation)
    DEV_MODE: bool = True

    @property
    def admin_ids(self) -> set[int]:
        return {int(x) for x in self.ADMIN_TELEGRAM_IDS.split(",") if x.strip().isdigit()}


settings = Settings()
