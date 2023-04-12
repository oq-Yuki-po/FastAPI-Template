import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.sql.ddl import CreateSchema, DropSchema
from sqlalchemy_utils import database_exists
from sqlalchemy_utils.functions.database import create_database

from app.main import app
from app.models import BaseModel, Engine, session


def remove_session() -> None:

    session.close()


@pytest.fixture(scope='session', autouse=True)
def setup_test_env(request):

    if not database_exists(Engine.url):
        create_database(Engine.url)

    schema_name: str = os.environ.get('DB_SCHEMA', 'test')

    stmt = CreateSchema(schema_name, if_not_exists=True)
    with Engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()

    def drop_schema():
        stmt = DropSchema(schema_name)
        with Engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    request.addfinalizer(drop_schema)

    return setup_test_env


def drop_all_tables():
    remove_session()
    BaseModel.metadata.drop_all(Engine)


@pytest.fixture(scope='function', autouse=True)
def setup_tables_at_function(request):

    BaseModel.metadata.drop_all(Engine)
    BaseModel.metadata.create_all(Engine)

    request.addfinalizer(drop_all_tables)

    return setup_tables_at_function


@pytest.fixture(scope='class', autouse=True)
def setup_tables_at_class(request):

    BaseModel.metadata.drop_all(Engine)
    BaseModel.metadata.create_all(Engine)

    request.addfinalizer(drop_all_tables)

    return setup_tables_at_class


@pytest.fixture()
def app_client():
    return TestClient(app)


@pytest.fixture()
def db_session(request):

    request.addfinalizer(remove_session)
    return session
