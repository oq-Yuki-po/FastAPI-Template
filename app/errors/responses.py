from typing import Union

from pydantic import BaseModel

from app.errors.message import ErrorMessage


class InternalServerErrorOut(BaseModel):

    message: str = ErrorMessage.INTERNAL_SERVER_ERROR


class InvalidRequestErrorOut(BaseModel):

    message: str = ErrorMessage.INVALID_REQUEST


class DataBaseErrorOut(BaseModel):

    message: str = ErrorMessage.DATABASE_ERROR


class DataBaseConnectionErrorOut(BaseModel):

    message: str = ErrorMessage.DATABASE_CONNECTION_ERROR


class Root500ErrorClass(BaseModel):
    __root__: Union[InternalServerErrorOut, DataBaseErrorOut, DataBaseConnectionErrorOut]


class BookAlreadyExistsErrorOut(BaseModel):

    message: str = ErrorMessage.BOOK_ALREADY_EXISTS


class BookNotFoundErrorOut(BaseModel):

    message: str = ErrorMessage.BOOK_NOT_FOUND


class ExternalApiErrorOut(BaseModel):

    message: str = ErrorMessage.EXTERNAL_API_ERROR
