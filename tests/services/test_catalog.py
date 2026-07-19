from datetime import date
from unittest.mock import AsyncMock, Mock

import pytest

from app.models import Author, Book
from app.schemas import BookCreate
from app.services import CatalogService, DuplicateIsbnError


def book_payload() -> BookCreate:
    return BookCreate(
        title="Service Book",
        isbn="9781449373320",
        author_name="Service Author",
        published_at=date(2026, 1, 1),
    )


async def test_create_book_rejects_duplicate_isbn() -> None:
    repository = Mock()
    repository.get_book_by_isbn = AsyncMock(return_value=Book())

    with pytest.raises(DuplicateIsbnError):
        await CatalogService(repository).create_book(book_payload())


async def test_create_book_reuses_existing_author() -> None:
    author = Author(id=1, name="Service Author")
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
