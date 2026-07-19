from sqlalchemy.exc import IntegrityError

from app.models import Author, Book
from app.repositories import CatalogRepository
from app.schemas import AuthorPage, AuthorRead, BookCreate, BookPage, BookRead


class DuplicateIsbnError(Exception):
    """Raised when a book ISBN is already registered."""


class CatalogService:
    def __init__(self, repository: CatalogRepository) -> None:
        self.repository = repository

    async def list_authors(self, offset: int, limit: int) -> AuthorPage:
        authors, total = await self.repository.list_authors(offset, limit)
        return AuthorPage(
            items=[AuthorRead.model_validate(author) for author in authors],
            total=total,
            offset=offset,
            limit=limit,
        )

    async def list_books(self, offset: int, limit: int) -> BookPage:
        books, total = await self.repository.list_books(offset, limit)
        return BookPage(
            items=[BookRead.model_validate(book) for book in books],
            total=total,
            offset=offset,
            limit=limit,
        )

    async def create_book(self, payload: BookCreate) -> Book:
        if await self.repository.get_book_by_isbn(payload.isbn) is not None:
            raise DuplicateIsbnError
        author = await self.repository.get_author_by_name(payload.author_name)
        if author is None:
            author = Author(name=payload.author_name)
            self.repository.add_author(author)
            await self.repository.flush()
        book = Book(
            title=payload.title,
            isbn=payload.isbn,
            author=author,
            cover_url=payload.cover_url,
            published_at=payload.published_at,
        )
        self.repository.add_book(book)
        try:
            await self.repository.commit()
        except IntegrityError as error:
            await self.repository.rollback()
            raise DuplicateIsbnError from error
        await self.repository.refresh_book(book)
        return book
