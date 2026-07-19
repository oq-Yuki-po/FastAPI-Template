from datetime import date
from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.exc import IntegrityError

from app.schemas import BookCreate
from app.services import CatalogService, DuplicateIsbnError
from tests.factories import AuthorFactory, BookCreateFactory, BookFactory


def book_payload() -> BookCreate:
    return BookCreateFactory.build(
        title="Service Book",
        isbn="9781449373320",
        author_name="Service Author",
        published_at=date(2026, 1, 1),
    )


async def test_create_book_rejects_duplicate_isbn() -> None:
    repository = Mock()
    repository.get_book_by_isbn = AsyncMock(return_value=BookFactory.build())

    with pytest.raises(DuplicateIsbnError):
        await CatalogService(repository).create_book(book_payload())


async def test_create_book_reuses_existing_author() -> None:
    author = AuthorFactory.build(id=1, name="Service Author")
    repository = Mock()
    repository.get_book_by_isbn = AsyncMock(return_value=None)
    repository.get_author_by_name = AsyncMock(return_value=author)
    repository.commit = AsyncMock()
    repository.refresh_book = AsyncMock()
    service = CatalogService(repository)

    created = await service.create_book(book_payload())

    assert created.author is author
    repository.add_author.assert_not_called()
    repository.add_book.assert_called_once_with(created)
    repository.commit.assert_awaited_once()


async def test_list_authors_maps_models_to_page() -> None:
    author = AuthorFactory.build(id=1)
    repository = Mock()
    repository.list_authors = AsyncMock(return_value=([author], 3))

    page = await CatalogService(repository).list_authors(offset=1, limit=1)

    assert page.model_dump() == {
        "items": [{"id": author.id, "name": author.name}],
        "total": 3,
        "offset": 1,
        "limit": 1,
    }


async def test_list_books_maps_models_to_page() -> None:
    book = BookFactory.build(id=1, author=AuthorFactory.build(id=2))
    repository = Mock()
    repository.list_books = AsyncMock(return_value=([book], 4))

    page = await CatalogService(repository).list_books(offset=2, limit=2)

    assert page.total == 4
    assert page.items[0].isbn == book.isbn
    assert page.items[0].author.id == book.author.id


async def test_create_book_creates_missing_author() -> None:
    repository = Mock()
    repository.get_book_by_isbn = AsyncMock(return_value=None)
    repository.get_author_by_name = AsyncMock(return_value=None)
    repository.flush = AsyncMock()
    repository.commit = AsyncMock()
    repository.refresh_book = AsyncMock()

    created = await CatalogService(repository).create_book(book_payload())

    assert created.author.name == "Service Author"
    repository.add_author.assert_called_once_with(created.author)
    repository.flush.assert_awaited_once()
    repository.add_book.assert_called_once_with(created)


async def test_create_book_rolls_back_integrity_conflict() -> None:
    repository = Mock()
    repository.get_book_by_isbn = AsyncMock(return_value=None)
    repository.get_author_by_name = AsyncMock(return_value=AuthorFactory.build())
    repository.commit = AsyncMock(
        side_effect=IntegrityError("INSERT books", {}, RuntimeError("duplicate"))
    )
    repository.rollback = AsyncMock()

    with pytest.raises(DuplicateIsbnError):
        await CatalogService(repository).create_book(book_payload())

    repository.rollback.assert_awaited_once()
    repository.refresh_book.assert_not_called()
