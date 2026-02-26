from __future__ import annotations

import asyncio
import logging
from collections import defaultdict

from app.events.models import ScrapeEvent

log = logging.getLogger(__name__)


class EventBus:
    """In-process pub/sub using asyncio.Queue per subscriber."""

    def __init__(self):
        self._subscribers: dict[str, list[asyncio.Queue]] = defaultdict(list)

    def subscribe(self, channel: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._subscribers[channel].append(queue)
        return queue

    def unsubscribe(self, channel: str, queue: asyncio.Queue):
        if channel in self._subscribers:
            self._subscribers[channel] = [q for q in self._subscribers[channel] if q is not queue]
            if not self._subscribers[channel]:
                del self._subscribers[channel]

    def publish(self, channel: str, event: ScrapeEvent):
        """Publish from a sync context (background thread) to async subscribers."""
        for queue in self._subscribers.get(channel, []):
            try:
                loop = asyncio.get_running_loop()
                loop.call_soon_threadsafe(queue.put_nowait, event)
            except RuntimeError:
                # No running loop — try direct put
                try:
                    queue.put_nowait(event)
                except asyncio.QueueFull:
                    log.warning(f"Event queue full for channel {channel}, dropping event")
            except asyncio.QueueFull:
                log.warning(f"Event queue full for channel {channel}, dropping event")
