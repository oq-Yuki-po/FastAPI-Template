import pytest

from app.errors.exceptions import BookAlreadyExistsError
from app.models.book import BookModel
from app.models.factories import AuthorFactory, BookFactory


class TestBookModel():

    def test_fetch_by_isbn(self, db_session):
        """
        test fetch_by_isbn
        """

        expected_isbn = "9784774142230"

        book = BookFactory(isbn=expected_isbn)
        db_session.add(book)
        db_session.commit()

        fetch_book = BookModel.fetch_by_isbn(expected_isbn)

        assert fetch_book is not None
        assert fetch_book.isbn == expected_isbn

    def test_fetch_by_isbn_data_is_none(self):
        """
        test fetch_by_isbn when data is None
        """

        fetch_book = BookModel.fetch_by_isbn("9784774142231")

        assert fetch_book is None

    def test_save_success(self, db_session):
        """
        test save
        """

        book = BookModel(title="test book",
                         isbn="9784774142232",
                         cover_path="test/path",
                         author=AuthorFactory()
                         )
        book_id = book.save()
        db_session.commit()

        assert book_id is not None
        assert book.id == book_id

    def test_save_duplicate(self, db_session):
        """
        test save when data is duplicated
        """

        expected_isbn = "9784774142233"

        book = BookFactory(isbn=expected_isbn)
        db_session.add(book)
        db_session.commit()

        duplicated_book = BookModel(title="test book",
                                    isbn=expected_isbn,
                                    cover_path="test/path",
                                    author=AuthorFactory()
                                    )

        with pytest.raises(BookAlreadyExistsError):
            duplicated_book.save()