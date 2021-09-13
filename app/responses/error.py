import traceback
from typing import Union

from fastapi import status
from pydantic import BaseModel


class ErrorMessage:
    INTERNAL_SERVER_ERROR = 'Internal Server Error'
    INVALID_REQUEST = 'Invalid Request'
    DATABASE_ERROR = 'DataBase Error'
    DATABASE_CONNECTION_ERROR = 'DataBase Connection Error'


class AppError(Exception):
    """App Base Exception
    """

    stacktrace: str = 'Stack Trace'
    code: str = 'Error Code'
    message: str = 'Error Message'


class InternalServerError(AppError):

    stacktrace: str = traceback.format_exc()
    code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = ErrorMessage.INTERNAL_SERVER_ERROR


class InternalServerErrorOut(BaseModel):

    stacktrace: str = traceback.format_exc()
    code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = ErrorMessage.INTERNAL_SERVER_ERROR


class InvalidRequestError(AppError):

    stacktrace: str = traceback.format_exc()
    code = status.HTTP_400_BAD_REQUEST
    message = ErrorMessage.INVALID_REQUEST


class InvalidRequestErrorOut(BaseModel):

    stacktrace: str = traceback.format_exc()
    code: int = status.HTTP_400_BAD_REQUEST
    message: str = ErrorMessage.INVALID_REQUEST


class DataBaseError(AppError):

    stacktrace: str = traceback.format_exc()
    code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = ErrorMessage.DATABASE_ERROR


class DataBaseErrorOut(BaseModel):

    stacktrace: str = traceback.format_exc()
    code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = ErrorMessage.DATABASE_ERROR


class DataBaseConnectionError(AppError):

    stacktrace: str = traceback.format_exc()
    code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = ErrorMessage.DATABASE_CONNECTION_ERROR


class DataBaseConnectionErrorOut(BaseModel):

    stacktrace: str = traceback.format_exc()
    code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = ErrorMessage.DATABASE_CONNECTION_ERROR


class Root500ErrorClass(BaseModel):
    __root__: Union[InternalServerErrorOut, DataBaseErrorOut, DataBaseConnectionErrorOut]
