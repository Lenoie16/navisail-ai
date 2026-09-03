"""Small in-process event bus used by the API and SSE subscribers."""

import asyncio
from collections import deque
from collections.abc import AsyncIterator
from uuid import UUID

from app.events.types import DomainEvent


class EventBus:
    def __init__(self, *, history_size: int = 256, queue_size: int = 128) -> None:
        self._history: deque[DomainEvent] = deque(maxlen=history_size)
        self._subscribers: dict[int, asyncio.Queue[DomainEvent]] = {}
        self._queue_size = queue_size
        self._next_subscriber = 0
        self._sequence = 0
        self._lock = asyncio.Lock()

    async def publish(self, event: DomainEvent) -> DomainEvent:
        async with self._lock:
            self._sequence = max(self._sequence + 1, event.sequence)
            event = event.model_copy(update={"sequence": self._sequence})
            self._history.append(event)
            for queue in self._subscribers.values():
                if not queue.full():
                    queue.put_nowait(event)
        return event

    async def subscribe(
        self, *, decision_session_id: UUID | None = None, last_event_id: UUID | None = None
    ) -> AsyncIterator[DomainEvent]:
        queue: asyncio.Queue[DomainEvent] = asyncio.Queue(maxsize=self._queue_size)
        async with self._lock:
            subscriber_id = self._next_subscriber
            self._next_subscriber += 1
            history = list(self._history)
            start = 0
            if last_event_id is not None:
                for index, event in enumerate(history):
                    if event.event_id == last_event_id:
                        start = index + 1
                        break
            replay = [
                event
                for event in history[start:]
                if decision_session_id is None or event.decision_session_id == decision_session_id
            ]
            self._subscribers[subscriber_id] = queue
        try:
            for event in replay:
                yield event
            while True:
                event = await queue.get()
                if decision_session_id is None or event.decision_session_id == decision_session_id:
                    yield event
        finally:
            async with self._lock:
                self._subscribers.pop(subscriber_id, None)


event_bus = EventBus()
