from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Rolewise API"
    environment: str = "development"
    api_prefix: str = "/api"
    frontend_url: str = "http://localhost:3000"
    database_url: str = "sqlite:///./rolewise.db"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = Field(default="development-only-change-me-at-least-32-chars")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    auth_cookie_secure: bool = False
    ai_rate_limit_per_minute: int = 20
    local_upload_dir: str = "./uploads"
    max_upload_bytes: int = 8 * 1024 * 1024
    llm_api_key: str | None = None
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4.1-mini"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
