import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_development_accepts_documented_defaults() -> None:
    assert Settings(_env_file=None).environment == "development"


def test_production_rejects_repository_secret() -> None:
    with pytest.raises(ValidationError, match="SECRET_KEY must be replaced"):
        Settings(_env_file=None, environment="production")


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
