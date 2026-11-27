"""Tests unitaires du modèle utilisateur initial."""

from unittest.mock import patch

from django.test import SimpleTestCase

from allelefounder.accounts.models import User


class UserManagerTests(SimpleTestCase):
    """Vérifie les invariants de création sans dépendre de la base."""

    @patch.object(User, "save")
    def test_create_user_normalizes_email(self, save) -> None:
        user = User.objects.create_user("Personne@EXAMPLE.COM", "secret-test")

        self.assertEqual(user.email, "Personne@example.com")
        self.assertTrue(user.check_password("secret-test"))
        save.assert_called_once_with(using=None)

    def test_create_user_rejects_empty_email(self) -> None:
        with self.assertRaisesRegex(ValueError, "obligatoire"):
            User.objects.create_user("")

    def test_superuser_rejects_missing_staff_status(self) -> None:
        with self.assertRaisesRegex(ValueError, "is_staff"):
            User.objects.create_superuser(
                "admin@example.com", "secret-test", is_staff=False
            )
