from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Author, Book
from app.repositories import CatalogRepository


async def test_catalog_repository_persists_and_lists_books(db_session: AsyncSession) -> None:
    repository = CatalogRepository(db_session)
    author = Author(name="Repository Author")
    repository.add_author(author)
    await repository.flush()
    book = Book(
        title="Repository Book",
        isbn="9781449373320",
        author=author,
        published_at=date(2026, 1, 1),
        cover_url=None,
    )
    repository.add_book(book)
    await repository.commit()

    books, total = await repository.list_books(offset=0, limit=10)

    assert total == 1
    assert books[0].author.name == author.name
    assert await repository.get_book_by_isbn(book.isbn) is book


async def test_catalog_repository_lists_and_finds_authors(db_session: AsyncSession) -> None:
    repository = CatalogRepository(db_session)
    authors = [Author(name="First Author"), Author(name="Second Author")]
    for author in authors:
        repository.add_author(author)
    await repository.commit()

    page, total = await repository.list_authors(offset=1, limit=1)

    assert total == 2
    assert page == [authors[1]]
    assert await repository.get_author_by_name(authors[0].name) is authors[0]
    assert await repository.get_author_by_name("Missing Author") is None


async def test_catalog_repository_rolls_back_pending_book(db_session: AsyncSession) -> None:
    repository = CatalogRepository(db_session)
    author = Author(name="Rollback Author")
    repository.add_author(author)
    await repository.flush()
    repository.add_book(
        Book(
            title="Rollback Book",
            isbn="9781449373320",
            author=author,
            published_at=date(2026, 1, 1),
        )
    )

    await repository.rollback()

    books, total = await repository.list_books(offset=0, limit=10)
    assert books == []
    assert total == 0
