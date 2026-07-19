from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Apply browser defense-in-depth headers to every application response."""

    def __init__(self, app: ASGIApp, *, production_mode: bool) -> None:
        super().__init__(app)
        self.production_mode = production_mode

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        # These headers are useful even for JSON APIs: error pages and future HTML
        # endpoints should not become MIME-sniffing or clickjacking entry points.
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

        if self.production_mode:
            # Production exposes no built-in documentation, so a deny-by-default CSP
            # can safely block accidental active content added to API responses.
            response.headers["Content-Security-Policy"] = (
                "default-src 'none'; frame-ancestors 'none'"
            )
            # TLS is terminated by the deployment edge. HSTS tells browsers never to
            # downgrade later requests after receiving one successful HTTPS response.
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response
