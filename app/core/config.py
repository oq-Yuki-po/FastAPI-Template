import os
from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None,
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
    allowed_hosts: list[str] = ["localhost", "127.0.0.1", "test", "testserver"]
    log_level: str = "INFO"

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        # Convenient defaults are limited to local/test environments so a deployment
        # cannot accidentally sign production tokens with a public repository secret.
        insecure_secrets = {
            "change-me-in-production-change-me-in-production",
            "development-only-secret-key-change-this-value",
        }
        secret_looks_like_placeholder = (
            self.secret_key in insecure_secrets
            or self.secret_key.lower().startswith(("replace", "change-me"))
        )
        if self.environment in {"staging", "production"} and secret_looks_like_placeholder:
            raise ValueError("SECRET_KEY must be replaced outside development and test")
        if self.environment in {"staging", "production"} and self.debug:
            raise ValueError("DEBUG must be disabled outside development and test")
        if self.environment == "production" and "postgres:postgres@" in self.database_url:
            raise ValueError("Default database credentials are forbidden in production")
        if "*" in self.cors_origins:
            raise ValueError("Wildcard CORS origins are incompatible with credentialed requests")
        if self.environment in {"staging", "production"} and "*" in self.allowed_hosts:
            raise ValueError("Wildcard ALLOWED_HOSTS is forbidden outside development and test")
        return self


def resolve_env_files() -> tuple[str, ...]:
    """Select dotenv files without embedding environment-specific values in code."""
    if env_file := os.getenv("ENV_FILE"):
        return (env_file,)
    environment = os.getenv("ENVIRONMENT", "development")
    return (".env", f".env.{environment}")


@lru_cache
def get_settings() -> Settings:
    # Process environment variables still take precedence over dotenv files,
    # which keeps container and secret-manager injection predictable.
    return Settings(_env_file=resolve_env_files())


settings = get_settings()
