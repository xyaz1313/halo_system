"""Structured JSON logging setup for the application and uvicorn loggers."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """Emit each log record as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "category": getattr(record, "category", record.name),
            "message": record.getMessage(),
        }
        # Include extra data dict if present
        data = getattr(record, "data", None)
        if data is not None:
            entry["data"] = data
        # Include exception info when available
        if record.exc_info and record.exc_info[0] is not None:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry)


def setup_logging(level: int = logging.INFO) -> None:
    """Configure structured JSON logging on root and uvicorn loggers.

    Call once during FastAPI lifespan startup.  Sets a single
    :class:`JSONFormatter` handler on each logger and disables propagation
    on uvicorn loggers to avoid double-logging.
    """
    formatter = JSONFormatter()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Root logger
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # Uvicorn loggers — own handler, no propagation
    for name in ("uvicorn", "uvicorn.access"):
        uv_logger = logging.getLogger(name)
        uv_logger.handlers.clear()
        uv_handler = logging.StreamHandler(sys.stdout)
        uv_handler.setFormatter(formatter)
        uv_logger.addHandler(uv_handler)
        uv_logger.propagate = False
