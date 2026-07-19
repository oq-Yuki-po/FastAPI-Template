from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


async def test_liveness(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_readiness(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_readiness_hides_database_error(
    client: AsyncClient, db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        db_session, "execute", AsyncMock(side_effect=RuntimeError("database credentials leaked"))
    )

    response = await client.get("/api/v1/health/ready")

    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}
    assert "credentials" not in response.text
