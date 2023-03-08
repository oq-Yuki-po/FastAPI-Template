from factory import Sequence
from factory.alchemy import SQLAlchemyModelFactory
from sqlalchemy import func

from app.models import AuthorModel, Engine, Session


class AuthorFactory(SQLAlchemyModelFactory):
    class Meta:

        model = AuthorModel
        sqlalchemy_session = Session()

    name = Sequence(lambda n: f'author_name_{n}')
    created_at = func.now()
    updated_at = func.now()
