"""Worker compatibility facade and process heartbeat helpers."""

from datetime import UTC, datetime
import redis

from app.core.config import settings
from app.jobs.tasks import orchestration_service


def publish_heartbeat() -> None:
    """Publish a short-lived worker heartbeat for operational monitoring."""
    client = redis.Redis.from_url(settings.redis_url)
    client.set(
        "navisail:worker:heartbeat",
        datetime.now(UTC).isoformat(),
        ex=max(30, int(settings.worker_heartbeat_seconds * 3)),
    )
    client.close()


__all__ = ["orchestration_service", "publish_heartbeat"]
