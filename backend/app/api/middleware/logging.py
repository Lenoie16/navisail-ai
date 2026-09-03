"""Request logging middleware."""

import logging
from time import perf_counter

from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("navisail.http")


class RequestLoggingMiddleware:
    """Log method, path, status, and elapsed time for HTTP requests."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        status_code = 500
        started = perf_counter()

        async def capture_status(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        await self.app(scope, receive, capture_status)
        logger.info(
            "%s %s %s %.2fms",
            scope.get("method"),
            scope.get("path"),
            status_code,
            (perf_counter() - started) * 1000,
        )
