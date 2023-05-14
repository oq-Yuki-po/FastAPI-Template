from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors.exceptions import BookAlreadyExistsError, BookNotFoundError, ExternalApiError
from app.models import AuthorModel, BookModel
from app.models.factories import BookFactory
from app.routers.setting import AppRoutes
from app.schemas.requests import BookSaveIn
from app.schemas.responses import BookGetAllOut, BookGetOut
from app.utils import ImageBase64

TEST_URL = f"{AppRoutes.API_VERSION}{AppRoutes.Books.PREFIX}"


def test_create_book_with_valid_data(app_client: TestClient, db_session: Session) -> None:
    """
    Test create_book with valid data
    """
    book_in = BookSaveIn(title="test title",
                         author_name="test author",
                         isbn="9784798157578",
                         cover_path="test/path")
    response = app_client.post(f"{TEST_URL}{AppRoutes.Books.POST_URL}", json=book_in.dict())
    saved_book = db_session.scalars(select(BookModel).where(BookModel.isbn == book_in.isbn)).first()
    saved_author = db_session.scalars(select(AuthorModel).where(AuthorModel.id == saved_book.author_id)).first()
    other_books = db_session.scalars(select(BookModel).where(BookModel.isbn != book_in.isbn)).all()
    other_authors = db_session.scalars(select(AuthorModel).where(AuthorModel.id != saved_book.author_id)).all()

    assert response.status_code == 200
    assert response.json() == {"message": "Book test title saved successfully"}
    assert saved_book.title == book_in.title
    assert saved_book.isbn == book_in.isbn
    assert saved_book.cover_path == book_in.cover_path
    assert saved_author.name == book_in.author_name
    assert len(other_books) == 0
    assert len(other_authors) == 0


def test_create_book_with_invalid_data(app_client: TestClient, db_session: Session) -> None:
    """
    Test create_book with invalid data
    """

    book = BookFactory(isbn="9784798157578")
    db_session.add(book)
    db_session.commit()

    book_in = BookSaveIn(title="test title",
                         author_name="test author",
                         isbn="9784798157578",
                         cover_path="test/path")
    response = app_client.post(f"{TEST_URL}{AppRoutes.Books.POST_URL}", json=book_in.dict())
    assert response.status_code == BookAlreadyExistsError.status_code
    assert response.json() == {"detail": BookAlreadyExistsError.message}


def test_create_book_openbd_valid_data(app_client: TestClient, mocker, db_session: Session) -> None:
    """
    Test create_book with valid data
    """

    test_title = "スタートライン : 一歩踏み出せば奇跡は起こる"
    test_author = "喜多川泰／著"
    test_isbn = "9784799311783"
    test_cover = "https://cover.openbd.jp/9784799311783.jpg"

    mock_obj = mocker.Mock()
    mock_obj.json.return_value = [
        {
            "summary": {
                "title": test_title,
                "author": test_author,
                "isbn": test_isbn,
                "cover": test_cover
            }
        }
    ]
    mocker.patch("app.api.book_info_fetcher.requests.get", return_value=mock_obj)
    mocker.patch("app.api.book_info_fetcher.BookInfo.save_image", return_value=f"test/path/{test_isbn}.jpg")

    response = app_client.post(f"{TEST_URL}{AppRoutes.Books.POST_OPENBD_URL}?isbn={test_isbn}")

    saved_book = db_session.scalars(select(BookModel).where(BookModel.isbn == test_isbn)).first()
    saved_author = db_session.scalars(select(AuthorModel).where(AuthorModel.id == saved_book.author_id)).first()
    other_books = db_session.scalars(select(BookModel).where(BookModel.isbn != test_isbn)).all()
    other_authors = db_session.scalars(select(AuthorModel).where(AuthorModel.id != saved_book.author_id)).all()

    assert response.status_code == 200
    assert response.json() == {"message": f"Book {test_title} saved successfully"}
    assert saved_book.title == test_title
    assert saved_book.isbn == test_isbn
    assert saved_book.cover_path == f"test/path/{test_isbn}.jpg"
    assert saved_author.name == test_author
    assert len(other_books) == 0
    assert len(other_authors) == 0


def test_create_book_openbd_invalid_data(app_client: TestClient, mocker) -> None:
    """
    Test create_book with invalid data
    """

    mocker.patch("app.api.book_info_fetcher.BookInfoFetcher.fetch", return_value=None)

    response = app_client.post(f"{TEST_URL}{AppRoutes.Books.POST_OPENBD_URL}?isbn=9784798157578")
    assert response.status_code == BookNotFoundError.status_code
    assert response.json() == {"detail": BookNotFoundError.message}


def test_create_book_openbd_book_already_exists(app_client: TestClient, mocker, db_session: Session) -> None:
    """
    Test create_book with book already exists
    """

    test_title = "スタートライン : 一歩踏み出せば奇跡は起こる"
    test_author = "喜多川泰／著"
    test_isbn = "9784799311783"
    test_cover = "https://cover.openbd.jp/9784799311783.jpg"

    mock_obj = mocker.Mock()
    mock_obj.json.return_value = [
        {
            "summary": {
                "title": test_title,
                "author": test_author,
                "isbn": test_isbn,
                "cover": test_cover
            }
        }
    ]
    mocker.patch("app.api.book_info_fetcher.requests.get", return_value=mock_obj)
    mocker.patch("app.api.book_info_fetcher.BookInfo.save_image", return_value=f"test/path/{test_isbn}.jpg")

    book = BookFactory(isbn=test_isbn)
    db_session.add(book)
    db_session.commit()

    response = app_client.post(f"{TEST_URL}{AppRoutes.Books.POST_OPENBD_URL}?isbn={test_isbn}")

    assert response.status_code == BookAlreadyExistsError.status_code
    assert response.json() == {"detail": BookAlreadyExistsError.message}


def test_create_book_openbd_external_api_error(app_client: TestClient, mocker) -> None:
    """
    Test create_book with external api error
    """

    mocker.patch("app.api.book_info_fetcher.BookInfoFetcher.fetch", side_effect=ExternalApiError)

    response = app_client.post(f"{TEST_URL}{AppRoutes.Books.POST_OPENBD_URL}?isbn=9784798157578")
    assert response.status_code == ExternalApiError.status_code
    assert response.json() == {"detail": ExternalApiError.message}


def test_get_books(app_client: TestClient, db_session: Session, make_image) -> None:
    """
    Test get_books
    """

    sample_image_path_1 = make_image("sample_1.png")
    sample_image_path_2 = make_image("sample_2.png")
    sample_image_path_3 = make_image("sample_3.png")

    book1 = BookFactory(cover_path=sample_image_path_1)
    book2 = BookFactory(cover_path=sample_image_path_2)
    book3 = BookFactory(cover_path=sample_image_path_3)

    db_session.add_all([book1, book2, book3])
    db_session.commit()

    response = app_client.get(f"{TEST_URL}{AppRoutes.Books.GET_URL}?offset=0&limit=10")

    expected_result = BookGetAllOut(books=[BookGetOut(id=i.id,
                                                      title=i.title,
                                                      author_name=i.authors.name,
                                                      cover_base64_image=ImageBase64.
                                                      encode(i.cover_path).decode("utf-8"),
                                                      isbn=i.isbn) for i in [book1, book2, book3]])
    assert response.status_code == 200
    assert response.json() == expected_result.dict()
