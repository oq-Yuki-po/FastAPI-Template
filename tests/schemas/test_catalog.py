import pytest
from pydantic import ValidationError

from tests.factories import BookCreateFactory


def test_book_requires_thirteen_digit_isbn() -> None:
    with pytest.raises(ValidationError):
        BookCreateFactory.build(isbn="not-an-isbn")


def test_book_factory_generates_valid_unique_isbns() -> None:
    books = BookCreateFactory.build_batch(3)

    assert len({book.isbn for book in books}) == 3
    assert all(len(book.isbn) == 13 and book.isbn.isdigit() for book in books)
