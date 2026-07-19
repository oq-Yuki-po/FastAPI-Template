from httpx import AsyncClient


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
    token = logged_in.json()["access_token"]

    current = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert current.status_code == 200
    assert current.json()["email"] == credentials["email"]


async def test_duplicate_registration_returns_conflict(client: AsyncClient) -> None:
    credentials = {"email": "duplicate@example.com", "password": "a-secure-password"}
    assert (await client.post("/api/v1/auth/register", json=credentials)).status_code == 201
    assert (await client.post("/api/v1/auth/register", json=credentials)).status_code == 409
