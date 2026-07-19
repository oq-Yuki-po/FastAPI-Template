from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "FastAPI Template"
    environment: Literal["development", "test", "staging", "production"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/app"
    secret_key: str = Field(
        default="change-me-in-production-change-me-in-production",
        min_length=32,
    )
    access_token_expire_minutes: int = 30
    jwt_issuer: str = "fastapi-template"
    jwt_audience: str = "fastapi-template-api"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    log_level: str = "INFO"

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        # Convenient defaults are limited to local/test environments so a deployment
        # cannot accidentally sign production tokens with a public repository secret.
        insecure_secrets = {
            "change-me-in-production-change-me-in-production",
            "development-only-secret-key-change-this-value",
        }
        if self.environment in {"staging", "production"} and self.secret_key in insecure_secrets:
            raise ValueError("SECRET_KEY must be replaced outside development and test")
        if self.environment in {"staging", "production"} and self.debug:
            raise ValueError("DEBUG must be disabled outside development and test")
        if self.environment == "production" and "postgres:postgres@" in self.database_url:
            raise ValueError("Default database credentials are forbidden in production")
        if "*" in self.cors_origins:
            raise ValueError("Wildcard CORS origins are incompatible with credentialed requests")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
