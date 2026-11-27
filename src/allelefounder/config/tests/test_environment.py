"""Tests de validation des variables d'environnement."""

from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from allelefounder.config.environment import boolean, integer, required


class EnvironmentTests(SimpleTestCase):
    """Vérifie les refus explicites de configuration invalide."""

    @patch.dict("os.environ", {}, clear=True)
    def test_required_rejects_missing_value(self) -> None:
        with self.assertRaisesRegex(ImproperlyConfigured, "EXAMPLE_SECRET"):
            required("EXAMPLE_SECRET")

    @patch.dict("os.environ", {"FEATURE": "peut-être"}, clear=True)
    def test_boolean_rejects_unknown_value(self) -> None:
        with self.assertRaisesRegex(ImproperlyConfigured, "booléen"):
            boolean("FEATURE", default=False)

    @patch.dict("os.environ", {"PORT": "70000"}, clear=True)
    def test_integer_enforces_bounds(self) -> None:
        with self.assertRaisesRegex(ImproperlyConfigured, "comprise"):
            integer("PORT", default=5432, minimum=1, maximum=65535)
