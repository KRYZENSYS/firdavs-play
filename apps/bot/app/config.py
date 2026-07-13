"""Bot config."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    BOT_TOKEN: str = ""
    BOT_USERNAME: str = "FirdavsPlayBot"
    WEBAPP_URL: str = "https://t.me/FirdavsPlayBot/play"
    APP_URL: str = "http://localhost:3000"
    API_URL: str = "http://api:8000"
    ADMIN_IDS: str = ""
    POLLING: bool = True
    LOG_LEVEL: str = "INFO"

    @property
    def admin_ids(self) -> list[int]:
        return [int(x) for x in self.ADMIN_IDS.split(",") if x.strip().isdigit()]


settings = Settings()
