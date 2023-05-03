from typing import Annotated

from fastapi import APIRouter, Query

from app import app_logger
from app.api.book_info_fetcher import BookInfoFetcher
from app.errors.custom_exception import CustomException
from app.errors.exceptions import BookAlreadyExistsError, BookNotFoundError, ExternalApiError
from app.errors.responses import BookAlreadyExistsErrorOut, BookNotFoundErrorOut, ExternalApiErrorOut, Root500ErrorClass
from app.models import AuthorModel, BookModel, session
from app.schemas.requests import BookSaveIn
from app.schemas.responses import BookGetAllOut, BookGetOut, BookSaveOut

router = APIRouter(
    prefix="/books",
    tags=["books"]
)


@router.post("/",
             response_model=BookSaveOut,
             responses={
                 409: {"model": BookAlreadyExistsErrorOut,
                       "description": "Book already exists"},
                 500: {"model": Root500ErrorClass,
                       "description": "Internal Server Error"}
             })
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

    CustomException
        If the book already exists in the database
    ```
    """
    try:

        author = AuthorModel(name=book_in.author_name)
        author_id = author.register()

        book = BookModel(title=book_in.title, author_id=author_id, isbn=book_in.isbn, cover_path=book_in.cover_path)
        book.save()
        session.commit()

        return BookSaveOut(message=f'Book {book_in.title} saved successfully')

    except BookAlreadyExistsError as error:
        app_logger.error(error.__class__.__name__)
        app_logger.error(error)
        session.rollback()
        raise CustomException(detail=error.message, status_code=error.status_code) from error


@router.post("/openbd",
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
    CustomException
        If the book already exists in the database
        Or if the book is not found in the OpenBD API
        Or if the OpenBD API returns an error response
        Or if the OpenBD API is not available
        Or if the OpenBD API returns an unexpected response
    ```
    """
    try:
        book_info = BookInfoFetcher(isbn).get_book_info()

        cover_path = book_info.save_image(directory_path="static/images")

        author = AuthorModel(name=book_info.author)
        author_id = author.register()

        book = BookModel(title=book_info.title, author_id=author_id, isbn=book_info.isbn, cover_path=cover_path)
        book.save()
        session.commit()

        return BookSaveOut(message=f'Book {book_info.title} saved successfully')

    except BookAlreadyExistsError as error:
        app_logger.error(error.__class__.__name__)
        app_logger.error(error)
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


@router.get("/",
            response_model=BookGetAllOut,
            responses={
                500: {"model": Root500ErrorClass,
                      "description": "Internal Server Error"}
            })
async def get_all_books(offset: int = Query(default=0, ge=0),
                        limit: int = Query(default=25, le=100)) -> BookGetAllOut:
    """
    get_all_books is a function that gets all books.

    ```
    Returns
    -------
    BookGetAllOut
        BookGetAllOut object
    ```
    """
    books = BookModel.fetch_all(offset=offset, limit=limit)

    return BookGetAllOut(books=[BookGetOut(id=i.id,
                                           title=i.title,
                                           author_name=i.author_name,
                                           isbn=i.isbn,
                                           ) for i in books])
