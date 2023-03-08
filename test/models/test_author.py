from sqlalchemy import select

from app.models import AuthorModel
from app.models.factories import AuthorFactory


class TestAuthorModel:

    def test_register_success(self, db_session):

        expected_name = "test author"

        author = AuthorModel(name=expected_name)
        registered_id = author.register()
        registered_author = db_session.scalars(select(AuthorModel).
                                               filter(AuthorModel.id == author.id)).\
            one()

        assert registered_author is not None
        assert registered_author.id == registered_id
        assert registered_author.name == expected_name

    def test_register_duplicate(self, db_session):

        expected_name = "test author"

        author = AuthorFactory(name=expected_name)
        db_session.add(author)
        db_session.commit()

        duplicated_author = AuthorModel(name=expected_name)
        duplicated_author_id = duplicated_author.register()

        assert author.id == duplicated_author_id

    def test_fetch_by_name_data_is_exist(self, db_session):

        expected_name = "test author"

        author = AuthorFactory(name=expected_name)
        db_session.add(author)
        db_session.commit()

        fetch_author = AuthorModel.fetch_by_name(name=expected_name)

        assert fetch_author is not None
        assert fetch_author.name == expected_name

    def test_fetch_by_name_data_is_none(self):

        fetch_author = AuthorModel.fetch_by_name(name="sample author")

        assert fetch_author is None

    def test_fetch_all_data_is_exist(self, db_session):

        expected_author_count = 10

        authors = AuthorFactory.create_batch(expected_author_count)
        db_session.add_all(authors)
        db_session.commit()

        fetch_authors = AuthorModel.fetch_all()

        assert len(fetch_authors) == expected_author_count

    def test_fetch_all_data_is_none(self):

        fetch_authors = AuthorModel.fetch_all()

        assert len(fetch_authors) == 0
