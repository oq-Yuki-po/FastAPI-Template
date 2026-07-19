from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models import User


async def test_register_login_and_current_user(client: AsyncClient) -> None:
    credentials = {"email": "dev@example.com", "password": "a-secure-password"}
    registered = await client.post("/api/v1/auth/register", json=credentials)
    assert registered.status_code == 201
    assert registered.json()["email"] == credentials["email"]

    logged_in = await client.post(
        "/api/v1/auth/token",
        data={"username": credentials["email"], "password": credentials["password"]},
    )
    assert logged_in.status_code == 200
    assert logged_in.headers["cache-control"] == "no-store"
    assert logged_in.headers["pragma"] == "no-cache"
    token = logged_in.json()["access_token"]

    current = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert current.status_code == 200
    assert current.json()["email"] == credentials["email"]


async def test_duplicate_registration_returns_conflict(client: AsyncClient) -> None:
    credentials = {"email": "duplicate@example.com", "password": "a-secure-password"}
    assert (await client.post("/api/v1/auth/register", json=credentials)).status_code == 201
    assert (await client.post("/api/v1/auth/register", json=credentials)).status_code == 409


async def test_login_rejects_wrong_password_without_account_details(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/token",
        data={"username": "missing@example.com", "password": "a-secure-password"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect email or password"}


async def test_login_rejects_inactive_user(client: AsyncClient, db_session: AsyncSession) -> None:
    db_session.add(
        User(
            email="inactive@example.com",
            hashed_password=hash_password("a-secure-password"),
            is_active=False,
        )
    )
    await db_session.commit()
    response = await client.post(
        "/api/v1/auth/token",
        data={"username": "inactive@example.com", "password": "a-secure-password"},
    )
    assert response.status_code == 401
