from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Author, Book


async def test_book_author_relationship(db_session: AsyncSession) -> None:
    author = Author(name="Martin Kleppmann")
    book = Book(
        title="Designing Data-Intensive Applications",
        isbn="9781449373320",
        published_at=date(2017, 3, 16),
        author=author,
    )
    db_session.add(book)
    await db_session.commit()

    saved = await db_session.scalar(select(Book).options(selectinload(Book.author)))
    assert saved is not None
    assert saved.author.name == author.name
