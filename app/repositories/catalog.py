from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Author, Book


class CatalogRepository:
    """Owns catalog persistence queries and hides SQLAlchemy from upper layers."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_authors(self, offset: int, limit: int) -> tuple[list[Author], int]:
        total = await self.session.scalar(select(func.count()).select_from(Author)) or 0
        query = select(Author).order_by(Author.id).offset(offset).limit(limit)
        return list((await self.session.scalars(query)).all()), total

    async def list_books(self, offset: int, limit: int) -> tuple[list[Book], int]:
        total = await self.session.scalar(select(func.count()).select_from(Book)) or 0
        query = (
            select(Book)
            .options(selectinload(Book.author))
            .order_by(Book.id)
            .offset(offset)
            .limit(limit)
        )
        return list((await self.session.scalars(query)).all()), total

    async def get_book_by_isbn(self, isbn: str) -> Book | None:
        books = await self.session.scalars(select(Book).where(Book.isbn == isbn))
        return books.first()

    async def get_author_by_name(self, name: str) -> Author | None:
        authors = await self.session.scalars(select(Author).where(Author.name == name))
        return authors.first()

    def add_author(self, author: Author) -> None:
        self.session.add(author)

    def add_book(self, book: Book) -> None:
        self.session.add(book)

    async def flush(self) -> None:
        await self.session.flush()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def refresh_book(self, book: Book) -> None:
        await self.session.refresh(book, attribute_names=["author"])
