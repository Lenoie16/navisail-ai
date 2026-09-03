"""Run the lightweight process-local worker heartbeat."""

from __future__ import annotations

import signal
import time

from app.core.config import settings
from app.core.logging import configure_logging
from app.jobs.workers import publish_heartbeat

running = True


def stop_worker(_signum: int, _frame: object) -> None:
    global running
    running = False


def main() -> None:
    configure_logging(settings.log_level)
    signal.signal(signal.SIGTERM, stop_worker)
    signal.signal(signal.SIGINT, stop_worker)
    while running:
        publish_heartbeat()
        time.sleep(settings.worker_heartbeat_seconds)


if __name__ == "__main__":
    main()
