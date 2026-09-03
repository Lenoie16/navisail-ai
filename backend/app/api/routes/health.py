"""Health endpoints."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
import redis
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.session import engine

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Report service liveness."""
    return {"status": "ok", "service": "navisail-ai"}


@router.get("/health/live")
async def live() -> dict[str, str]:
    """Report process liveness without requiring external dependencies."""
    return {"status": "ok", "service": "navisail-ai"}


@router.get("/health/ready", response_model=None)
async def ready() -> dict[str, str] | JSONResponse:
    """Report whether required persistence dependencies are reachable."""
    checks: dict[str, str] = {}
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except SQLAlchemyError:
        checks["database"] = "unavailable"
    try:
        client = redis.Redis.from_url(
            settings.redis_url,
            socket_connect_timeout=settings.redis_health_timeout_seconds,
            socket_timeout=settings.redis_health_timeout_seconds,
        )
        client.ping()
        client.close()
        checks["redis"] = "ok"
    except (redis.RedisError, OSError):
        checks["redis"] = "unavailable"
    if all(value == "ok" for value in checks.values()):
        return {"status": "ready", **checks}
    return JSONResponse(status_code=503, content={"status": "not_ready", **checks})


@router.get("/health/worker", response_model=None)
async def worker_health() -> dict[str, str] | JSONResponse:
    """Report whether the worker heartbeat is recent."""
    client = redis.Redis.from_url(
        settings.redis_url,
        socket_connect_timeout=settings.redis_health_timeout_seconds,
        socket_timeout=settings.redis_health_timeout_seconds,
    )
    try:
        heartbeat = client.get("navisail:worker:heartbeat")
        if heartbeat:
            return {"status": "ok", "last_heartbeat": heartbeat.decode()}
        return JSONResponse(status_code=503, content={"status": "stale"})
    except (redis.RedisError, OSError):
        return JSONResponse(status_code=503, content={"status": "unavailable"})
    finally:
        client.close()


@router.get("/version")
async def version() -> dict[str, str]:
    """Return the running application version."""
    return {"service": "navisail-ai", "version": settings.app_version}
