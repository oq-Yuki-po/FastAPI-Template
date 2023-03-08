import random

import factory
from factory import Sequence
from factory.alchemy import SQLAlchemyModelFactory
from sqlalchemy import func

from app.models import BookModel, Engine, Session
from app.models.factories.author import AuthorFactory


class BookFactory(SQLAlchemyModelFactory):
    class Meta:

        model = BookModel
        sqlalchemy_session = Session()

    title = Sequence(lambda n: f'book_title_{n}')
    isbn = Sequence(lambda n: str(random.randrange(10**12, 10**13)))
    cover_path = Sequence(lambda n: f'book_cover_path_{n}.png')
    authors = factory.SubFactory(AuthorFactory)
    created_at = func.now()
    updated_at = func.now()
