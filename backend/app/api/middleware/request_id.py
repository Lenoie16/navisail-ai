"""Request correlation middleware."""

from uuid import uuid4
from contextvars import ContextVar

from starlette.types import ASGIApp, Message, Receive, Scope, Send


request_id_context: ContextVar[str] = ContextVar("navisail_request_id", default="")


class RequestIdMiddleware:
    """Attach a correlation ID to every request and response."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        request_id = headers.get(b"x-request-id", uuid4().hex.encode()).decode()
        scope["navisail.request_id"] = request_id
        token = request_id_context.set(request_id)

        async def send_with_request_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                message.setdefault("headers", []).append((b"x-request-id", request_id.encode()))
            await send(message)

        try:
            await self.app(scope, receive, send_with_request_id)
        finally:
            request_id_context.reset(token)
