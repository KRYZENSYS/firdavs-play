"""Application settings loaded from environment variables."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "FirdavsPlay"
    APP_ENV: str = "development"
    APP_URL: str = "http://localhost:3000"
    API_URL: str = "http://localhost:8000"
    WS_URL: str = "ws://localhost:8000"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str = "postgresql+asyncpg://firdavs:firdavs@db:5432/firdavs_play"
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_CACHE_URL: str = "redis://redis:6379/1"

    JWT_SECRET: str = "dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_MIN: int = 10080

    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_BOT_USERNAME: str = "FirdavsPlayBot"
    TELEGRAM_WEBAPP_URL: str = ""
    TELEGRAM_INIT_DATA_SECRET: str = "dev-secret"

    RATE_LIMIT_PER_MIN: int = 60
    ANTI_CHEAT_ENABLED: bool = True
    PROVABLY_FAIR_ENABLED: bool = True

    BOT_ADMIN_IDS: str = ""

    DEFAULT_COINS: int = 1000
    DAILY_BONUS: int = 100
    WEEKLY_BONUS: int = 1000
    MIN_BET: int = 10
    MAX_BET: int = 100000
    HOUSE_EDGE: float = 0.04

    @property
    def admin_ids(self) -> list[int]:
        return [int(x) for x in self.BOT_ADMIN_IDS.split(",") if x.strip().isdigit()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
