from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.dependencies import get_event_bus
from app.events.bus import EventBus
from app.services.auth_service import decode_token

router = APIRouter()


@router.get("/scrape/{job_id}")
async def scrape_events(
    job_id: int,
    token: str = Query(..., description="JWT access token (EventSource can't set headers)"),
    event_bus: EventBus = Depends(get_event_bus),
):
    # Validate JWT from query param
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token")

    async def event_generator():
        channel = f"job:{job_id}"
        queue = event_bus.subscribe(channel)
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"event: {event.type}\ndata: {json.dumps(event.data)}\n\n"

                    if event.type in ("completed", "failed", "cancelled"):
                        break
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            event_bus.unsubscribe(channel, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
