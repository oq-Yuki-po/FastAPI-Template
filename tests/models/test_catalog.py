from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Book
from tests.factories import BookFactory


async def test_book_author_relationship(db_session: AsyncSession) -> None:
    book = BookFactory.build(
        author__name="Martin Kleppmann",
        title="Designing Data-Intensive Applications",
    )
    db_session.add(book)
    await db_session.commit()

    saved = await db_session.scalar(select(Book).options(selectinload(Book.author)))
    assert saved is not None
    assert saved.author.name == "Martin Kleppmann"
