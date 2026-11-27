"""Tests des pages et contrôles de santé."""

from unittest.mock import MagicMock, patch

from django.db import DatabaseError
from django.test import SimpleTestCase
from django.urls import reverse


class HealthTests(SimpleTestCase):
    """Distingue la santé du processus de celle de PostgreSQL."""

    def test_home_is_available(self) -> None:
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AlleleFounder")

    def test_liveness_does_not_query_database(self) -> None:
        with patch("allelefounder.config.views.connection") as database:
            response = self.client.get(reverse("health-live"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "service": "web"})
        self.assertEqual(response["Cache-Control"], "no-store")
        database.cursor.assert_not_called()

    @patch("allelefounder.config.views.connection")
    def test_readiness_accepts_available_database(self, database) -> None:
        database_cursor = MagicMock()
        database.cursor.return_value.__enter__.return_value = database_cursor

        response = self.client.get(reverse("health-ready"))

        self.assertEqual(response.status_code, 200)
        database_cursor.execute.assert_called_once_with("SELECT 1")

    @patch("allelefounder.config.views.connection")
    def test_readiness_rejects_unavailable_database(self, database) -> None:
        database.cursor.side_effect = DatabaseError(
            "detail that must not reach the response"
        )
        response = self.client.get(reverse("health-ready"))

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {"status": "unavailable", "dependency": "postgresql"},
        )
        self.assertNotContains(response, "detail", status_code=503)

    def test_request_id_is_a_uuid(self) -> None:
        response = self.client.get(reverse("health-live"), HTTP_X_REQUEST_ID="bad")

        self.assertRegex(
            response["X-Request-ID"],
            r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
        )
