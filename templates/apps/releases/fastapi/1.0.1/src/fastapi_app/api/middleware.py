"""Bounded request admission, safe correlation and relative redirects."""

import logging
import secrets
import time
import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from fastapi_app.settings import Settings


class Admission:
    """Use constant memory for one process-wide fixed admission window."""

    limit: int
    window: float
    clock: Callable[[], float]
    started: float
    count: int

    def __init__(
        self, settings: Settings, clock: Callable[[], float] = time.monotonic
    ) -> None:
        """Initialize a finite counter without storing client identities."""
        self.limit = settings.request_limit
        self.window = settings.window_seconds
        self.clock = clock
        self.started = clock()
        self.count = 0

    def allow(self) -> bool:
        """Admit up to the limit, resetting the window after its deadline."""
        now = self.clock()
        if now - self.started >= self.window:
            self.started, self.count = now, 0
        if self.count >= self.limit:
            return False
        self.count += 1
        return True


class RequestMiddleware(BaseHTTPMiddleware):
    """Emit safe request events and enforce development admission bounds."""

    settings: Settings
    logger: logging.Logger
    admission: Admission

    def __init__(
        self,
        app: Callable[..., Awaitable[None]],
        settings: Settings,
        logger: logging.Logger,
        admission: Admission,
    ) -> None:
        """Inject shared settings, logger and the bounded admission object."""
        super().__init__(app)
        self.settings, self.logger, self.admission = (
            settings,
            logger,
            admission,
        )

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Handle responses/errors without recording user-controlled contents."""
        response: Response
        started = time.monotonic()
        request_id = uuid.uuid4().hex
        nonce = secrets.token_urlsafe(24)
        request.state.nonce = nonce
        limited = request.method != "OPTIONS" and request.url.path.startswith(
            self.settings.prefix + "/api/"
        )
        try:
            if limited and not self.admission.allow():
                response = JSONResponse(
                    {"detail": "Request limit reached."},
                    status_code=429,
                    headers={
                        "Retry-After": str(
                            int(self.settings.window_seconds) + 1
                        )
                    },
                )
            else:
                response = await call_next(request)
        except Exception:
            response = JSONResponse(
                {"detail": "Internal application error."}, status_code=500
            )
        route = getattr(request.scope.get("route"), "path", "unmatched")
        self.logger.log(
            logging.ERROR if response.status_code >= 500 else logging.INFO,
            "http_request",
            extra={
                "request_id": request_id,
                "method": (
                    request.method
                    if request.method
                    in {
                        "GET",
                        "POST",
                        "PUT",
                        "PATCH",
                        "DELETE",
                        "OPTIONS",
                        "HEAD",
                    }
                    else "OTHER"
                ),
                "route": route,
                "status": response.status_code,
                "duration_ms": round((time.monotonic() - started) * 1000, 3),
            },
        )
        response.headers.update(
            {
                "X-Request-ID": request_id,
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "Referrer-Policy": "no-referrer",
                "Content-Security-Policy": f"default-src 'self'; script-src 'self' 'nonce-{nonce}'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'none'",
            }
        )
        return response
