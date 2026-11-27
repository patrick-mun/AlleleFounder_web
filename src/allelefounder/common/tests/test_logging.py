"""Tests de non-divulgation de la journalisation structurée."""

import json
import logging
import sys

from django.test import SimpleTestCase

from allelefounder.common.logging import SafeJsonFormatter


class SafeJsonFormatterTests(SimpleTestCase):
    """Vérifie que les messages libres ne sortent jamais dans les journaux."""

    def test_redacts_arbitrary_message_and_exception_detail(self) -> None:
        try:
            raise ValueError("identité sensible")
        except ValueError:
            record = logging.LogRecord(
                "allelefounder.test",
                logging.ERROR,
                __file__,
                1,
                "message libre avec génotype",
                (),
                exc_info=sys.exc_info(),
            )

        payload = SafeJsonFormatter().format(record)

        self.assertNotIn("génotype", payload)
        self.assertNotIn("identité sensible", payload)
        self.assertEqual(json.loads(payload)["event"], "log.event_redacted")
        self.assertEqual(json.loads(payload)["exception_type"], "ValueError")

    def test_keeps_controlled_event_code(self) -> None:
        record = logging.LogRecord(
            "allelefounder.test",
            logging.INFO,
            __file__,
            1,
            "account.created",
            (),
            exc_info=None,
        )

        payload = json.loads(SafeJsonFormatter().format(record))

        self.assertEqual(payload["event"], "account.created")
