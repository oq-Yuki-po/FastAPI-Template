import pytest
from pydantic import ValidationError

from app.schemas import BookCreate


def test_book_requires_thirteen_digit_isbn() -> None:
    with pytest.raises(ValidationError):
        BookCreate(
            title="A book",
            isbn="not-an-isbn",
            author_name="An author",
            published_at="2026-01-01",
        )
