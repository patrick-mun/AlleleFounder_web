"""Gestionnaires du modèle utilisateur."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib.auth.base_user import BaseUserManager

if TYPE_CHECKING:
    from .models import User


class UserManager(BaseUserManager):
    """Crée les utilisateurs identifiés uniquement par leur courriel."""

    use_in_migrations = True

    def create_user(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> User:
        """Crée et enregistre un utilisateur standard."""
        if not email:
            raise ValueError("Une adresse électronique est obligatoire.")

        normalized_email = self.normalize_email(email)
        user = self.model(email=normalized_email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> User:
        """Crée un administrateur en vérifiant ses attributs obligatoires."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Un superutilisateur doit avoir is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Un superutilisateur doit avoir is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
