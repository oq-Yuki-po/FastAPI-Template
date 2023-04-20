from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app import app_logger
from app.errors.custom_exception import CustomException
from app.errors.message import ErrorMessage


class ExceptionMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        try:
            await self.app(scope, receive, send)
        except HTTPException as exc:
            app_logger.error(exc.message)
            response = exc.to_response()
            await response(scope, receive, send)
        except CustomException as exc:
            app_logger.error(exc.__class__.__name__)
            app_logger.error(exc.message)
            response = JSONResponse(status_code=exc.status_code,
                                    content={"message": exc.message})
            await response(scope, receive, send)
        except SQLAlchemyError as exc:
            app_logger.error(exc.__class__.__name__)
            app_logger.error(str(exc))
            response = JSONResponse(status_code=500,
                                    content={"message": ErrorMessage.INTERNAL_SERVER_ERROR})
            await response(scope, receive, send)
        except OSError as exc:
            app_logger.error(str(exc))
            app_logger.error(exc.__class__.__name__)
            response = JSONResponse(status_code=500,
                                    content={"message": ErrorMessage.INTERNAL_SERVER_ERROR})
            await response(scope, receive, send)
        except Exception as exc:
            app_logger.error(exc.__class__.__name__)
            app_logger.error(str(exc))
            response = JSONResponse(status_code=500,
                                    content={"message": ErrorMessage.INTERNAL_SERVER_ERROR})
            await response(scope, receive, send)
