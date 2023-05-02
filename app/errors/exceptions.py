from fastapi import status

from app.errors.message import ErrorMessage


class AppError(Exception):
    """App Base Exception
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = 'Error Message'


class InternalServerError(AppError):

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = ErrorMessage.INTERNAL_SERVER_ERROR


class InvalidRequestError(AppError):

    status_code: int = status.HTTP_400_BAD_REQUEST
    message: str = ErrorMessage.INVALID_REQUEST


class DataBaseError(AppError):

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = ErrorMessage.DATABASE_ERROR


class DataBaseConnectionError(AppError):

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = ErrorMessage.DATABASE_CONNECTION_ERROR


class BookAlreadyExistsError(AppError):

    status_code: int = status.HTTP_409_CONFLICT
    message: str = ErrorMessage.BOOK_ALREADY_EXISTS


class BookNotFoundError(AppError):

    status_code: int = status.HTTP_404_NOT_FOUND
    message: str = ErrorMessage.BOOK_NOT_FOUND


class ExternalApiError(AppError):

    status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE
    message: str = ErrorMessage.EXTERNAL_API_ERROR
