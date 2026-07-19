from datetime import timedelta

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password
from tests.factories import UserCreateFactory, UserFactory


async def test_register_login_and_current_user(client: AsyncClient) -> None:
    credentials = UserCreateFactory.build(
        email="dev@example.com", password="a-secure-password"
    ).model_dump(mode="json")
    registered = await client.post("/api/v1/auth/register", json=credentials)
    assert registered.status_code == 201
    assert registered.json() == {
        "id": 1,
        "email": credentials["email"],
        "is_active": True,
        "is_superuser": False,
    }
    assert "password" not in registered.json()
    assert "hashed_password" not in registered.json()

    logged_in = await client.post(
        "/api/v1/auth/token",
        data={"username": credentials["email"], "password": credentials["password"]},
    )
    assert logged_in.status_code == 200
    assert logged_in.headers["cache-control"] == "no-store"
    assert logged_in.headers["pragma"] == "no-cache"
    assert logged_in.json()["token_type"] == "bearer"
    token = logged_in.json()["access_token"]

    current = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert current.status_code == 200
    assert current.json()["email"] == credentials["email"]


async def test_duplicate_registration_returns_conflict(client: AsyncClient) -> None:
    credentials = {"email": "duplicate@example.com", "password": "a-secure-password"}
    assert (await client.post("/api/v1/auth/register", json=credentials)).status_code == 201
    duplicate = await client.post("/api/v1/auth/register", json=credentials)
    assert duplicate.status_code == 409
    assert duplicate.json() == {"detail": "Email already registered"}


async def test_registration_normalizes_email(client: AsyncClient) -> None:
    credentials = {"email": "Developer@EXAMPLE.COM", "password": "a-secure-password"}

    response = await client.post("/api/v1/auth/register", json=credentials)

    assert response.status_code == 201
    assert response.json()["email"] == "developer@example.com"


async def test_registration_rejects_short_password(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "dev@example.com", "password": "too-short"},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "password"]


async def test_login_rejects_wrong_password_without_account_details(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/token",
        data={"username": "missing@example.com", "password": "a-secure-password"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect email or password"}
    assert response.headers["www-authenticate"] == "Bearer"


async def test_login_rejects_wrong_password_for_existing_user(client: AsyncClient) -> None:
    credentials = {"email": "dev@example.com", "password": "a-secure-password"}
    await client.post("/api/v1/auth/register", json=credentials)

    response = await client.post(
        "/api/v1/auth/token",
        data={"username": credentials["email"], "password": "a-different-password"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect email or password"}


async def test_login_rejects_inactive_user(client: AsyncClient, db_session: AsyncSession) -> None:
    user = UserFactory.build(
        email="inactive@example.com",
        hashed_password=hash_password("a-secure-password"),
        is_active=False,
    )
    db_session.add(user)
    await db_session.commit()
    response = await client.post(
        "/api/v1/auth/token",
        data={"username": "inactive@example.com", "password": "a-secure-password"},
    )
    assert response.status_code == 401


async def test_current_user_rejects_expired_token(client: AsyncClient) -> None:
    token = create_access_token(1, expires_delta=timedelta(seconds=-1))

    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
    assert response.headers["www-authenticate"] == "Bearer"


async def test_current_user_rejects_inactive_user(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    user = UserFactory.build(is_active=False)
    db_session.add(user)
    await db_session.commit()
    token = create_access_token(user.id)

    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
