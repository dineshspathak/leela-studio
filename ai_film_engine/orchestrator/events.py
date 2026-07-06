import asyncio
from collections.abc import Callable
from typing import Any


class EventBus:
    def __init__(self):
        self._listeners: dict[str, list[Callable[[str, Any], Any]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[str, Any], Any]):
        """Subscribe to a specific event type."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    async def emit(self, event_type: str, data: Any):
        """Dispatch event asynchronously to all registered listeners."""
        if event_type in self._listeners:
            tasks = []
            for cb in self._listeners[event_type]:
                if asyncio.iscoroutinefunction(cb):
                    tasks.append(cb(event_type, data))
                else:
                    # Run sync callbacks in thread pool to avoid blocking async event loop
                    tasks.append(asyncio.to_thread(cb, event_type, data))
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
