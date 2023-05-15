from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Query
from fastapi_versioning import version

from app import app_logger, handle_errors
from app.api.book_info_fetcher import BookInfoFetcher
from app.errors.custom_exception import CustomException
from app.errors.exceptions import BookAlreadyExistsError, BookNotFoundError, ExternalApiError
from app.errors.responses import BookAlreadyExistsErrorOut, BookNotFoundErrorOut, ExternalApiErrorOut, Root500ErrorClass
from app.models import AuthorModel, BookModel, session
from app.routers.setting import AppRoutes
from app.schemas.requests import BookSaveIn
from app.schemas.responses import BookGetAllOut, BookGetOut, BookSaveOut
from app.utils.image_convert import ImageBase64

router = APIRouter(
    prefix=AppRoutes.Books.PREFIX,
    tags=[AppRoutes.Books.TAG],
)


@router.post(AppRoutes.Books.POST_URL,
             response_model=BookSaveOut,
             responses={
                 409: {"model": BookAlreadyExistsErrorOut,
                       "description": "Book already exists"},
                 500: {"model": Root500ErrorClass,
                       "description": "Internal Server Error"}
             })
@handle_errors
@version(1, 0)
async def create_book(book_in: BookSaveIn) -> BookSaveOut:
    """
    create_book is a function that creates a book.

    ```
    Parameters
    ----------
    book_in : BookSaveIn
        Book Information from user input (title, author_name, isbn, cover_path)

    Returns
    -------
    BookSaveOut
        BookSaveOut object

    Raises
    ------
    BookAlreadyExistsError
        If the book already exists in the database
    ```
    """
    try:

        datetime.strptime(book_in.published_at, '%Y-%m-%d')

        author = AuthorModel(name=book_in.author_name)
        author_id = author.register()

        book = BookModel(title=book_in.title,
                         author_id=author_id,
                         isbn=book_in.isbn,
                         cover_path=book_in.cover_path,
                         published_at=book_in.published_at)
        book.save()
        session.commit()

        return BookSaveOut(message=f'Book {book_in.title} saved successfully')

    except BookAlreadyExistsError as error:
        app_logger.error(error.__class__.__name__)
        session.rollback()
        raise CustomException(detail=error.message, status_code=error.status_code) from error
    except ValueError as error:
        session.rollback()
        raise CustomException(detail='published_at must be YYYY-MM-DD format', status_code=500) from error
    finally:
        session.close()


@router.post(AppRoutes.Books.POST_OPENBD_URL,
             response_model=BookSaveOut,
             responses={
                 404: {"model": BookNotFoundErrorOut,
                       "description": "Book not found"},
                 409: {"model": BookAlreadyExistsErrorOut,
                       "description": "Book already exists"},
                 500: {"model": Root500ErrorClass,
                       "description": "Internal Server Error"},
                 503: {"model": ExternalApiErrorOut,
                       "description": "External API Error"}
             })
@handle_errors
@version(1, 0)
async def create_book_openbd(isbn: Annotated[str,
                                             Query(title="ISBN code",
                                                   min_length=13,
                                                   max_length=13)]) -> BookSaveOut:
    """
    create_book_openbd is a function that creates a book using OpenBD API.

    ```
    Parameters
    ----------
    isbn : str
        ISBN code of the book

    Returns
    -------
    BookSaveOut
        BookSaveOut object

    Raises
    ------
    BookAlreadyExistsError
        If the book already exists in the database
    BookNotFoundError
        If the book is not found in the OpenBD API
    ExternalApiError
        If the OpenBD API returns an error response
        Or if the OpenBD API is not available
        Or if the OpenBD API returns an unexpected response
    ```
    """
    try:
        book_info = BookInfoFetcher(isbn).get_book_info()

        cover_path = book_info.save_image(directory_path="static/images")

        author = AuthorModel(name=book_info.author)
        author_id = author.register()

        book = BookModel(title=book_info.title,
                         author_id=author_id,
                         isbn=book_info.isbn,
                         cover_path=cover_path,
                         published_at=book_info.published_at)
        book.save()
        session.commit()

        return BookSaveOut(message=f'Book {book_info.title} saved successfully')

    except BookAlreadyExistsError as error:
        app_logger.error(error.__class__.__name__)
        session.rollback()
        raise CustomException(detail=error.message, status_code=error.status_code) from error

    except BookNotFoundError as error:
        app_logger.error(error.__class__.__name__)
        session.rollback()
        raise CustomException(detail=error.message, status_code=error.status_code) from error

    except ExternalApiError as error:
        app_logger.error(error.__class__.__name__)
        session.rollback()
        raise CustomException(detail=error.message, status_code=error.status_code) from error
    finally:
        session.close()


@router.get(AppRoutes.Books.GET_URL,
            response_model=BookGetAllOut,
            responses={
                500: {"model": Root500ErrorClass,
                      "description": "Internal Server Error"}
            })
@handle_errors
@version(1, 0)
async def get_all_books(offset: int = Query(default=0,
                                            ge=0,
                                            description="offset of the book list"),
                        limit: int = Query(default=25,
                                           ge=1,
                                           le=100,
                                           description="limit of the book list")) -> BookGetAllOut:
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
        books = BookModel.fetch_all(offset=offset, limit=limit)

        return BookGetAllOut(books=[BookGetOut(id=i.id,
                                               title=i.title,
                                               author_name=i.author_name,
                                               cover_base64_image=ImageBase64.encode(i.cover_path),
                                               isbn=i.isbn,
                                               published_at=str(i.published_at.isoformat())
                                               ) for i in books])
    finally:
        session.close()
