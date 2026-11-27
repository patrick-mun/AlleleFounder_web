"""Modèles des comptes AlleleFounder."""

from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    """Utilisateur authentifié par une adresse électronique unique."""

    username = None
    email = models.EmailField("adresse électronique", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()

    def __str__(self) -> str:
        """Retourne l'identifiant non ambigu du compte."""
        return self.email
