from fastapi import APIRouter, Query
from fastapi_versioning import version

from app import handle_errors
from app.errors.responses import Root500ErrorClass
from app.models import AuthorModel, session
from app.routers.setting import AppRoutes
from app.schemas.responses import AuthorGetAllOut, AuthorGetOut

router = APIRouter(
    prefix=AppRoutes.Authors.PREFIX,
    tags=[AppRoutes.Authors.TAG],
)


@router.get(AppRoutes.Books.GET_URL,
            response_model=AuthorGetAllOut,
            responses={
                500: {"model": Root500ErrorClass,
                      "description": "Internal Server Error"}
            })
@handle_errors
@version(1, 0)
async def get_all_authors(offset: int = Query(default=0,
                                              ge=0,
                                              description="offset of the author list"),
                          limit: int = Query(default=25,
                                             ge=1,
                                             le=100,
                                             description="limit of the author list")) -> AuthorGetAllOut:
    """
    get_all_books is a function that gets all books.

    ```
    Returns
    -------
    BookGetAllOut
        BookGetAllOut object
    ```
    """
    try:
        authors = AuthorModel.fetch_all(offset, limit)

        return AuthorGetAllOut(authors=[AuthorGetOut(id=i.id, author_name=i.name) for i in authors])
    finally:
        session.close()
