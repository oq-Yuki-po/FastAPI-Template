from httpx import AsyncClient


async def test_invalid_bearer_token_is_rejected(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
