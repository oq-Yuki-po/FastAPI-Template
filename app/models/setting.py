import os
from datetime import datetime

from sqlalchemy import Column, DateTime, MetaData, create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, declared_attr, scoped_session, sessionmaker
from sqlalchemy_utils import create_database, database_exists

from app import app_logger
from app.errors.exceptions import DataBaseConnectionError, InternalServerError

# Engine
SERVER = os.getenv('POSTGRES_SERVER')
USER = os.getenv('POSTGRES_USER')
PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB = os.getenv('POSTGRES_DB')
PORT = os.getenv('POSTGRES_PORT')

Engine = create_engine(
    f"postgresql://{USER}:{PASSWORD}@{SERVER}:{PORT}/{DB}",
    echo=False
)

# Session
session = scoped_session(
    sessionmaker(Engine, autoflush=False, autocommit=False)
)


class Base():
    """BaseModel Class

    Attributes
    -------
    created_at : Column

    updated_at : Column
    """

    __table_args__ = {'schema': os.environ.get('DB_SCHEMA', None)}

    @declared_attr
    def created_at(self):
        return Column(DateTime, default=datetime.now, nullable=False)

    @declared_attr
    def updated_at(self):
        return Column(DateTime, default=datetime.now, nullable=False)


schema_name: str = os.environ.get('DB_SCHEMA', 'public')

metadata = MetaData(naming_convention={
    'pk': 'pk_%(table_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'ix': 'ix_%(table_name)s_%(column_0_name)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
}, schema=schema_name)

BaseModel = declarative_base(cls=Base, metadata=metadata)


def initialize_db() -> None:
    try:
        if not database_exists(Engine.url):
            app_logger.info('Create Database')
            create_database(Engine.url)
    except SQLAlchemyError as exception:
        app_logger.error(exception)
        raise DataBaseConnectionError() from exception
    except Exception as exception:
        app_logger.error(exception)
        raise InternalServerError() from exception


def initialize_table() -> None:
    try:
        with Engine.connect() as conn:
            inspector = inspect(conn)
            if 'books' in inspector.get_table_names():
                app_logger.info("Table exists")
            else:
                app_logger.info('Create Table')
                BaseModel.metadata.create_all(Engine)
    except SQLAlchemyError as exception:
        app_logger.error(exception)
        raise DataBaseConnectionError() from exception
    except Exception as exception:
        app_logger.error(exception)
        raise InternalServerError() from exception
