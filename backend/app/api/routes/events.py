"""Server-sent event stream for decision-session updates."""

import asyncio
from collections.abc import AsyncIterator
from uuid import UUID

from fastapi import APIRouter, Header, Query
from fastapi.responses import StreamingResponse

from app.events.subscriber import subscribe_events
from app.core.performance import measure, metrics_store

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/stream")
async def stream_events(
    decision_session_id: UUID | None = Query(default=None),
    last_event_id: UUID | None = Header(default=None, alias="Last-Event-ID"),
) -> StreamingResponse:
    async def body() -> AsyncIterator[str]:
        yield ": connected\n\n"
        events = subscribe_events(
            decision_session_id=decision_session_id,
            last_event_id=last_event_id,
        )
        try:
            while True:
                try:
                    event = await asyncio.wait_for(anext(events), timeout=20)
                except TimeoutError:
                    yield ": keepalive\n\n"
                    continue
                with measure("sse.delivery", metrics_store):
                    yield f"id: {event.event_id}\nevent: {event.event_type}\ndata: {event.sse_data()}\n\n"
        finally:
            await events.aclose()

    return StreamingResponse(
        body(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )
