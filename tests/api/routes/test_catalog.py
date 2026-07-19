import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import AuthorFactory, BookFactory


async def test_catalog_lists_are_empty_by_default(client: AsyncClient) -> None:
    books = await client.get("/api/v1/books")
    authors = await client.get("/api/v1/authors")

    assert books.status_code == 200
    assert books.json() == {"items": [], "total": 0, "offset": 0, "limit": 25}
    assert authors.status_code == 200
    assert authors.json() == {"items": [], "total": 0, "offset": 0, "limit": 25}


async def test_create_and_list_book(
    client: AsyncClient,
    authenticated_headers: dict[str, str],
    book_payload: dict[str, object],
) -> None:
    created = await client.post(
        "/api/v1/books", json=book_payload, headers=authenticated_headers
    )

    assert created.status_code == 201
    assert created.json() == {
        "id": 1,
        "title": book_payload["title"],
        "isbn": book_payload["isbn"],
        "cover_url": book_payload["cover_url"],
        "published_at": book_payload["published_at"],
        "author": {"id": 1, "name": book_payload["author_name"]},
    }

    books = await client.get("/api/v1/books")
    assert books.status_code == 200
    assert books.json()["total"] == 1
    assert books.json()["items"][0] == created.json()

    authors = await client.get("/api/v1/authors")
    assert authors.status_code == 200
    assert authors.json()["items"] == [{"id": 1, "name": book_payload["author_name"]}]


async def test_create_book_requires_authentication(
    client: AsyncClient, book_payload: dict[str, object]
) -> None:
    response = await client.post("/api/v1/books", json=book_payload)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


async def test_create_book_rejects_duplicate_isbn(
    client: AsyncClient,
    authenticated_headers: dict[str, str],
    book_payload: dict[str, object],
) -> None:
    first = await client.post(
        "/api/v1/books", json=book_payload, headers=authenticated_headers
    )
    duplicate = await client.post(
        "/api/v1/books", json=book_payload, headers=authenticated_headers
    )

    assert first.status_code == 201
    assert duplicate.status_code == 409
    assert duplicate.json() == {"detail": "ISBN already registered"}


async def test_create_book_reuses_existing_author(
    client: AsyncClient,
    authenticated_headers: dict[str, str],
    book_payload: dict[str, object],
) -> None:
    first = await client.post(
        "/api/v1/books", json=book_payload, headers=authenticated_headers
    )
    second_payload = {**book_payload, "title": "Another book", "isbn": "9781449373320"}
    second = await client.post(
        "/api/v1/books", json=second_payload, headers=authenticated_headers
    )

    authors = await client.get("/api/v1/authors")
    assert first.status_code == 201
    assert second.status_code == 201
    assert second.json()["author"]["id"] == first.json()["author"]["id"]
    assert authors.json()["total"] == 1


@pytest.mark.parametrize(
    ("field", "invalid_value"),
    [
        ("title", ""),
        ("isbn", "not-an-isbn"),
        ("author_name", ""),
        ("published_at", "not-a-date"),
        ("cover_url", "x" * 2049),
    ],
)
async def test_create_book_validates_payload(
    client: AsyncClient,
    authenticated_headers: dict[str, str],
    book_payload: dict[str, object],
    field: str,
    invalid_value: object,
) -> None:
    response = await client.post(
        "/api/v1/books",
        json={**book_payload, field: invalid_value},
        headers=authenticated_headers,
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", field]


async def test_book_pagination_returns_stable_page_and_full_total(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    author = AuthorFactory.build()
    books = BookFactory.build_batch(3, author=author)
    db_session.add_all(books)
    await db_session.commit()

    response = await client.get("/api/v1/books", params={"offset": 1, "limit": 1})

    assert response.status_code == 200
    assert response.json()["total"] == 3
    assert response.json()["offset"] == 1
    assert response.json()["limit"] == 1
    assert [item["id"] for item in response.json()["items"]] == [books[1].id]


async def test_author_pagination_beyond_results_returns_empty_page(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    db_session.add_all(AuthorFactory.build_batch(2))
    await db_session.commit()

    response = await client.get("/api/v1/authors", params={"offset": 10, "limit": 5})

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 2, "offset": 10, "limit": 5}


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/books?offset=-1",
        "/api/v1/books?limit=0",
        "/api/v1/books?limit=101",
        "/api/v1/authors?offset=-1",
        "/api/v1/authors?limit=0",
        "/api/v1/authors?limit=101",
    ],
)
async def test_catalog_pagination_rejects_out_of_range_values(
    client: AsyncClient, path: str
) -> None:
    response = await client.get(path)

    assert response.status_code == 422
