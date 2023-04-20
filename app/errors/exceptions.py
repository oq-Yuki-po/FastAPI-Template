import traceback

from fastapi import status

from app.errors.message import ErrorMessage


class AppError(Exception):
    """App Base Exception
    """

    stacktrace: str = 'Stack Trace'
    status_code: str = 'Error Code'
    message: str = 'Error Message'


class InternalServerError(AppError):

    stacktrace: str = traceback.format_exc()
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = ErrorMessage.INTERNAL_SERVER_ERROR


class InvalidRequestError(AppError):

    stacktrace: str = traceback.format_exc()
    status_code = status.HTTP_400_BAD_REQUEST
    message = ErrorMessage.INVALID_REQUEST


class DataBaseError(AppError):

    stacktrace: str = traceback.format_exc()
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = ErrorMessage.DATABASE_ERROR


class DataBaseConnectionError(AppError):

    stacktrace: str = traceback.format_exc()
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = ErrorMessage.DATABASE_CONNECTION_ERROR


class BookAlreadyExistsError(AppError):

    stacktrace: str = traceback.format_exc()
    status_code: int = status.HTTP_409_CONFLICT
    message: str = ErrorMessage.BOOK_ALREADY_EXISTS

class BookNotFoundError(AppError):

    stacktrace: str = traceback.format_exc()
    status_code: int = status.HTTP_404_NOT_FOUND
    message: str = ErrorMessage.BOOK_NOT_FOUND

class ExternalApiError(AppError):

    stacktrace: str = traceback.format_exc()
    status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE
    message: str = ErrorMessage.EXTERNAL_API_ERROR
