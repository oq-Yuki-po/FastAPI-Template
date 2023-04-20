from fastapi import APIRouter

from app import app_logger
from app.errors.custom_exception import CustomException
from app.errors.exceptions import BookAlreadyExistsError
from app.errors.responses import BookAlreadyExistsErrorOut, Root500ErrorClass
from app.models import AuthorModel, BookModel, session
from app.schemas.requests import BookSaveIn
from app.schemas.responses import BookSaveOut

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
    try:

        author = AuthorModel(name=book_in.author_name)
        author_id = author.register()

        book = BookModel(title=book_in.title, author_id=author_id, isbn=book_in.isbn, cover_path=book_in.cover_path)
        book.save()
        session.commit()

        return BookSaveOut(message=f'Book {book_in.title} saved successfully')

    except BookAlreadyExistsError as error:
        session.rollback()
        raise CustomException(message=error.message, status_code=error.status_code) from error
