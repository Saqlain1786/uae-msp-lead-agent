from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "UAE MSP Lead Agent"
    environment: str = "development"
    database_path: str = "app/data/leads.db"

    scheduler_enabled: bool = True
    scheduler_hour_utc: int = Field(default=5, ge=0, le=23)
    scheduler_minute_utc: int = Field(default=0, ge=0, le=59)

    reasoner_save_threshold: float = Field(default=0.55, ge=0, le=1)
    discovery_mode: str = "mock"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
