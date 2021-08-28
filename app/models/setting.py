import os
from datetime import datetime

from sqlalchemy import Column, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker

# Engine
SERVER = os.getenv('POSTGRES_SERVER')
USER = os.getenv('POSTGRES_USER')
PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB = os.getenv('POSTGRES_DB')
PORT = os.getenv('POSTGRES_PORT')

Engine = create_engine(
    "postgresql://{}:{}@{}:{}/{}".format(USER, PASSWORD, SERVER, PORT, DB),
    encoding="utf-8",
    echo=False
)

# Session
session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=Engine
)


class Base(object):
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=datetime.now, nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=datetime.now, nullable=False)


BaseModel = declarative_base(cls=Base)
