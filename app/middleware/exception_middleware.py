from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app import app_logger
from app.errors.message import ErrorMessage


class ExceptionMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:

        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        response_started = False

        async def sender(message: Message) -> None:
            nonlocal response_started

            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, receive, sender)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            app_logger.error(exc)
            response = JSONResponse(status_code=500,
                                    content={"detail": ErrorMessage.INTERNAL_SERVER_ERROR})
            if not response_started:
                await response(scope, receive, send)
