from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession
from app.models import Author, Book
from app.schemas import AuthorPage, AuthorRead, BookCreate, BookPage, BookRead

router = APIRouter(tags=["catalog"])


@router.get("/authors", response_model=AuthorPage)
async def list_authors(
    db: DbSession,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=25, ge=1, le=100),
) -> AuthorPage:
    total = await db.scalar(select(func.count()).select_from(Author)) or 0
    query = select(Author).order_by(Author.id).offset(offset).limit(limit)
    authors = (await db.scalars(query)).all()
    return AuthorPage(
        items=[AuthorRead.model_validate(author) for author in authors],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/books", response_model=BookPage)
async def list_books(
    db: DbSession,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=25, ge=1, le=100),
) -> BookPage:
    total = await db.scalar(select(func.count()).select_from(Book)) or 0
    query = (
        select(Book)
        .options(selectinload(Book.author))
        .order_by(Book.id)
        .offset(offset)
        .limit(limit)
    )
    books = (await db.scalars(query)).all()
    return BookPage(
        items=[BookRead.model_validate(book) for book in books],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.post("/books", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(payload: BookCreate, db: DbSession, _current_user: CurrentUser) -> Book:
    if await db.scalar(select(Book.id).where(Book.isbn == payload.isbn)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="ISBN already registered")
    author = await db.scalar(select(Author).where(Author.name == payload.author_name))
    if author is None:
        author = Author(name=payload.author_name)
        db.add(author)
        await db.flush()
    book = Book(
        title=payload.title,
        isbn=payload.isbn,
        author=author,
        cover_url=payload.cover_url,
        published_at=payload.published_at,
    )
    db.add(book)
    await db.commit()
    await db.refresh(book, attribute_names=["author"])
    return book
