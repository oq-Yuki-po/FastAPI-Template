from httpx import AsyncClient


async def authenticated_headers(client: AsyncClient) -> dict[str, str]:
    credentials = {"email": "books@example.com", "password": "a-secure-password"}
    await client.post("/api/v1/auth/register", json=credentials)
    response = await client.post(
        "/api/v1/auth/token",
        data={"username": credentials["email"], "password": credentials["password"]},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def test_create_and_list_book(client: AsyncClient) -> None:
    headers = await authenticated_headers(client)
    payload = {
        "title": "Designing Data-Intensive Applications",
        "isbn": "9781449373320",
        "author_name": "Martin Kleppmann",
        "cover_url": None,
        "published_at": "2017-03-16",
    }
    created = await client.post("/api/v1/books", json=payload, headers=headers)
    assert created.status_code == 201
    assert created.json()["author"]["name"] == payload["author_name"]

    books = await client.get("/api/v1/books")
    assert books.status_code == 200
    assert books.json()["total"] == 1
    assert books.json()["items"][0]["isbn"] == payload["isbn"]

    authors = await client.get("/api/v1/authors")
    assert authors.json()["total"] == 1


async def test_create_book_requires_authentication(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/books",
        json={
            "title": "A book",
            "isbn": "9781449373320",
            "author_name": "An author",
            "published_at": "2026-01-01",
        },
    )
    assert response.status_code == 401
