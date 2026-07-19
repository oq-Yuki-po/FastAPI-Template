import pytest
from pydantic import ValidationError

from app.core.config import Settings, resolve_env_files


def test_development_accepts_documented_defaults() -> None:
    assert Settings(_env_file=None).environment == "development"


def test_environment_selects_matching_dotenv(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ENV_FILE", raising=False)
    monkeypatch.setenv("ENVIRONMENT", "test")

    assert resolve_env_files() == ("config/env/base.env", "config/env/test.env")


def test_explicit_env_file_takes_precedence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV_FILE", "/run/secrets/app.env")

    assert resolve_env_files() == ("/run/secrets/app.env",)


def test_production_rejects_repository_secret() -> None:
    with pytest.raises(ValidationError, match="SECRET_KEY must be replaced"):
        Settings(
            _env_file=None,
            environment="production",
            secret_key="change-me-in-production-change-me-in-production",
            database_url="postgresql+asyncpg://app:private@db:5432/app",
        )


def test_production_rejects_placeholder_secret() -> None:
    with pytest.raises(ValidationError, match="SECRET_KEY must be replaced"):
        Settings(
            _env_file=None,
            environment="production",
            secret_key="replace-with-a-random-production-secret-at-least-32-characters",
            database_url="postgresql+asyncpg://app:private@db:5432/app",
        )


def test_production_accepts_private_secret() -> None:
    config = Settings(
        _env_file=None,
        environment="production",
        secret_key="a-private-production-secret-with-sufficient-entropy",
        database_url="postgresql+asyncpg://app:private@db:5432/app",
    )
    assert config.environment == "production"


def test_credentialed_cors_rejects_wildcard_origin() -> None:
    with pytest.raises(ValidationError, match="Wildcard CORS"):
        Settings(_env_file=None, cors_origins=["*"])


def test_production_rejects_wildcard_allowed_host() -> None:
    with pytest.raises(ValidationError, match="Wildcard ALLOWED_HOSTS"):
        Settings(
            _env_file=None,
            environment="production",
            secret_key="a-private-production-secret-with-sufficient-entropy",
            database_url="postgresql+asyncpg://app:private@db:5432/app",
            allowed_hosts=["*"],
        )


def test_production_rejects_debug_mode() -> None:
    with pytest.raises(ValidationError, match="DEBUG must be disabled"):
        Settings(
            _env_file=None,
            environment="production",
            secret_key="a-private-production-secret-with-sufficient-entropy",
            database_url="postgresql+asyncpg://app:private@db:5432/app",
            debug=True,
        )


def test_production_rejects_default_database_credentials() -> None:
    with pytest.raises(ValidationError, match="Default database credentials"):
        Settings(
            _env_file=None,
            environment="production",
            secret_key="a-private-production-secret-with-sufficient-entropy",
        )
