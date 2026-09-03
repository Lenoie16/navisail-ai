"""FastAPI application entry point."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from collections import defaultdict, deque
from time import monotonic
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware.logging import RequestLoggingMiddleware
from app.api.middleware.request_id import RequestIdMiddleware
from app.api.routes import routers
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.performance import measure, metrics_store


def create_app() -> FastAPI:
    configure_logging(settings.log_level)
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs" if settings.enable_docs else None,
        redoc_url="/redoc" if settings.enable_docs else None,
    )
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_url],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    rate_windows: dict[str, deque[float]] = defaultdict(deque)

    @app.middleware("http")
    async def rate_limit(request: Request, call_next):
        if request.url.path.startswith("/api/") and request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            now = monotonic()
            client = request.client.host if request.client else "unknown"
            window = rate_windows[client]
            while window and now - window[0] >= 60:
                window.popleft()
            if len(window) >= settings.rate_limit_per_minute:
                return JSONResponse(status_code=429, content={"detail": "rate limit exceeded"})
            window.append(now)
        with measure("http.request", metrics_store):
            return await call_next(request)
    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
        return response
    for router in routers:
        app.include_router(router, prefix="/api/v1")
    return app


app = create_app()
