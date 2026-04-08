"""In-process event bus — dict-based singleton with publish/subscribe/unsubscribe."""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Callable

logger = logging.getLogger("halo.events")

# Handler type: callable that accepts **kwargs
Handler = Callable[..., Any]


class EventBus:
    """Simple synchronous publish/subscribe event bus.

    Handlers are stored in a dict mapping event type strings to handler lists.
    Exceptions in handlers are caught and logged — they never propagate to the
    publisher.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Handler) -> None:
        """Register *handler* for *event_type*."""
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Handler) -> None:
        """Remove *handler* from *event_type*.  Idempotent — no error if not found."""
        try:
            self._handlers[event_type].remove(handler)
        except ValueError:
            pass

    def publish(self, event_type: str, **data: Any) -> None:
        """Emit an event.  Calls every registered handler for *event_type*.

        Handler exceptions are caught and logged so one failing handler does
        not prevent subsequent handlers from executing.
        """
        for handler in list(self._handlers.get(event_type, [])):
            try:
                handler(event_type=event_type, **data)
            except Exception:
                logger.exception(
                    "Handler %r failed for event %s", handler, event_type
                )

    def reset(self) -> None:
        """Clear all subscriptions.  Intended for test isolation."""
        self._handlers.clear()


# Module-level singleton — each worker process gets its own instance.
bus = EventBus()
