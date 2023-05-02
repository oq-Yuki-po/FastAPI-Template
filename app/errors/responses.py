from dataclasses import dataclass
from typing import Union

from pydantic import BaseModel

from app.errors.message import ErrorMessage


@dataclass
class InternalServerErrorOut(BaseModel):

    detail: str = ErrorMessage.INTERNAL_SERVER_ERROR


@dataclass
class InvalidRequestErrorOut(BaseModel):

    detail: str = ErrorMessage.INVALID_REQUEST


@dataclass
class DataBaseErrorOut(BaseModel):

    detail: str = ErrorMessage.DATABASE_ERROR


@dataclass
class DataBaseConnectionErrorOut(BaseModel):

    detail: str = ErrorMessage.DATABASE_CONNECTION_ERROR


@dataclass
class Root500ErrorClass(BaseModel):
    __root__: Union[InternalServerErrorOut, DataBaseErrorOut, DataBaseConnectionErrorOut]


@dataclass
class BookAlreadyExistsErrorOut(BaseModel):

    detail: str = ErrorMessage.BOOK_ALREADY_EXISTS


@dataclass
class BookNotFoundErrorOut(BaseModel):

    detail: str = ErrorMessage.BOOK_NOT_FOUND


@dataclass
class ExternalApiErrorOut(BaseModel):

    detail: str = ErrorMessage.EXTERNAL_API_ERROR
