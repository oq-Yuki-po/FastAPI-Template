import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.router import api_router
from app.core.config import Settings, settings
from app.core.logging import configure_logging
from app.core.middleware import SecurityHeadersMiddleware

configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    logger.info("Application starting")
    yield
    logger.info("Application stopping")


def create_app(config: Settings = settings) -> FastAPI:
    production_mode = config.environment in {"staging", "production"}
    application = FastAPI(
        title=config.app_name,
        version="1.0.0",
        debug=config.debug,
        lifespan=lifespan,
        # Schema endpoints reveal the complete attack surface. They remain useful
        # locally but are disabled in externally reachable environments.
        docs_url=None if production_mode else "/docs",
        redoc_url=None if production_mode else "/redoc",
        openapi_url=None if production_mode else "/openapi.json",
    )
    application.add_middleware(
        TrustedHostMiddleware,
        # Reject forged Host headers before URL generation, redirects, or future
        # password-reset links can reflect an attacker-controlled domain.
        allowed_hosts=config.allowed_hosts,
    )
    application.add_middleware(SecurityHeadersMiddleware, production_mode=production_mode)
    application.add_middleware(
        CORSMiddleware,
        # Origins are explicit because credentialed CORS must never reflect an
        # arbitrary caller. Settings validation rejects the wildcard form.
        allow_origins=config.cors_origins,
        allow_credentials=True,
        # Only methods and request headers used by the current API are permitted.
        # Expand this allowlist deliberately when adding endpoints.
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )
    application.include_router(api_router, prefix=config.api_v1_prefix)

    @application.exception_handler(Exception)
    async def unhandled_exception(_request: Request, error: Exception) -> JSONResponse:
        logger.exception("Unhandled application error", exc_info=error)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    return application


app = create_app()
