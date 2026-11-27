"""Journalisation JSON à surface volontairement limitée."""

import contextvars
import json
import logging
import os
import re
from datetime import UTC, datetime

request_id_context: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default=""
)
SAFE_EVENT_PATTERN = re.compile(r"^[a-z][a-z0-9_.-]{0,127}$")


class SafeJsonFormatter(logging.Formatter):
    """Produit un JSON sans sérialiser les attributs libres du journal."""

    def format(self, record: logging.LogRecord) -> str:
        """Formate les champs techniques explicitement autorisés."""
        event = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "service": "allelefounder-web",
            "release": os.environ.get("APP_RELEASE", "development"),
            "event": self._safe_event(record),
        }
        request_id = request_id_context.get()
        if request_id:
            event["request_id"] = request_id
        if record.exc_info:
            event["exception_type"] = record.exc_info[0].__name__
        return json.dumps(event, ensure_ascii=False, separators=(",", ":"))

    @staticmethod
    def _safe_event(record: logging.LogRecord) -> str:
        """N'accepte que des codes d'événement, jamais une charge arbitraire."""
        if isinstance(record.msg, str) and SAFE_EVENT_PATTERN.fullmatch(record.msg):
            return record.msg
        return "log.event_redacted"
