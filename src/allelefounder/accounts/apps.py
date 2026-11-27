"""Configuration de l'application des comptes."""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Déclare l'application des comptes."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "allelefounder.accounts"
    label = "accounts"
    verbose_name = "Comptes"

    def ready(self) -> None:
        """Branche les signaux d'audit de sécurité."""
        from . import signals  # noqa: F401
