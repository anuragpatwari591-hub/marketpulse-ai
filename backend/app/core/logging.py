"""Structured JSON logging. Never log secrets (API keys, tokens, passwords)."""
import json
import logging
import sys
import time
import uuid
from contextvars import ContextVar

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")

_REDACT_KEYS = {"api_key", "token", "password", "secret", "authorization"}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "module": record.name,
            "message": record.getMessage(),
            "request_id": request_id_ctx.get(),
        }
        if record.exc_info:
            payload["error"] = self.formatException(record.exc_info)
        extra = getattr(record, "extra_fields", None)
        if extra:
            for k, v in extra.items():
                if k.lower() in _REDACT_KEYS:
                    continue
                payload[k] = v
        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)


def new_request_id() -> str:
    return uuid.uuid4().hex[:12]
