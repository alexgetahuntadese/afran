from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Smart Hospital & Office IT Management Platform"
    environment: str = "development"
    secret_key: str = Field(default="change-me-in-production", min_length=16)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    database_url: str = "sqlite+aiosqlite:///./smart_it.db"
    redis_url: str = "redis://localhost:6379/0"
    scan_interval_seconds: int = 30
    trial_days: int = 14
    trial_max_devices: int = 10
    trial_remote_session_minutes: int = 10
    backend_host: str = "127.0.0.1"
    backend_port: int = 8080

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
