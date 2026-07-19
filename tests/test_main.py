from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.main import app, create_app


def test_openapi_contains_versioned_routes() -> None:
    paths = app.openapi()["paths"]
    assert "/api/v1/auth/token" in paths
    assert "/api/v1/books" in paths


async def test_responses_include_browser_security_headers(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/live")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["permissions-policy"] == "camera=(), microphone=(), geolocation=()"


async def test_production_disables_docs_and_enables_strict_headers() -> None:
    config = Settings(
        _env_file=None,
        environment="production",
        secret_key="a-private-production-secret-with-sufficient-entropy",
        database_url="postgresql+asyncpg://app:private@db:5432/app",
        allowed_hosts=["api.example.com"],
    )
    production_app = create_app(config)
    assert production_app.docs_url is None
    assert production_app.redoc_url is None
    assert production_app.openapi_url is None

    async with AsyncClient(
        transport=ASGITransport(app=production_app), base_url="https://api.example.com"
    ) as client:
        response = await client.get("/api/v1/health/live")

    assert response.headers["strict-transport-security"].startswith("max-age=31536000")
    assert response.headers["content-security-policy"] == (
        "default-src 'none'; frame-ancestors 'none'"
    )


async def test_untrusted_host_is_rejected() -> None:
    config = Settings(_env_file=None, allowed_hosts=["api.example.com"])
    restricted_app = create_app(config)
    async with AsyncClient(
        transport=ASGITransport(app=restricted_app), base_url="http://attacker.example"
    ) as client:
        response = await client.get("/api/v1/health/live")

    assert response.status_code == 400
