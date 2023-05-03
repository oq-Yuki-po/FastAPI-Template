from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.errors.custom_exception import CustomException
from app.errors.message import ErrorMessage


class ExceptionMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        try:
            await self.app(scope, receive, send)
        except CustomException as exc:
            response = JSONResponse(status_code=exc.status_code,
                                    content={"detail": exc.detail})
            await response(scope, receive, send)
        except HTTPException as exc:
            response = JSONResponse(status_code=exc.status_code,
                                    content={"detail": exc.detail})
            await response(scope, receive, send)
        except SQLAlchemyError as exc:
            response = JSONResponse(status_code=500,
                                    content={"message": ErrorMessage.INTERNAL_SERVER_ERROR})
            await response(scope, receive, send)
        except OSError as exc:
            response = JSONResponse(status_code=500,
                                    content={"message": ErrorMessage.INTERNAL_SERVER_ERROR})
            await response(scope, receive, send)
        except Exception as exc: # pylint: disable=broad-exception-caught
            response = JSONResponse(status_code=500,
                                    content={"message": ErrorMessage.INTERNAL_SERVER_ERROR})
            await response(scope, receive, send)
