from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CatalogServiceDep, CurrentUser
from app.models import Book
from app.schemas import AuthorPage, BookCreate, BookPage, BookRead
from app.services import DuplicateIsbnError

router = APIRouter(tags=["catalog"])


@router.get("/authors", response_model=AuthorPage)
async def list_authors(
    service: CatalogServiceDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=25, ge=1, le=100),
) -> AuthorPage:
    return await service.list_authors(offset, limit)


@router.get("/books", response_model=BookPage)
async def list_books(
    service: CatalogServiceDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=25, ge=1, le=100),
) -> BookPage:
    return await service.list_books(offset, limit)


@router.post("/books", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(
    payload: BookCreate, service: CatalogServiceDep, _current_user: CurrentUser
) -> Book:
    try:
        return await service.create_book(payload)
    except DuplicateIsbnError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="ISBN already registered"
        ) from error
