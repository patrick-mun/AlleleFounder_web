"""Modèles d'identité, d'organisation et d'autorisation AlleleFounder."""

from __future__ import annotations

import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

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


class Organization(models.Model):
    """Frontière de gouvernance et d'isolation des données."""

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        DISABLED = "DISABLED", "Désactivée"

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField("nom", max_length=180)
    status = models.CharField(
        "état", max_length=16, choices=Status.choices, default=Status.ACTIVE
    )
    created_at = models.DateTimeField("créée le", auto_now_add=True)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Membership(models.Model):
    """Adhésion active d'un utilisateur à une organisation avec un rôle."""

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrateur"
        ANALYST = "ANALYST", "Analyste"
        REVIEWER = "REVIEWER", "Relecteur"
        READER = "READER", "Lecteur"

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.PROTECT, related_name="memberships"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="memberships"
    )
    role = models.CharField("rôle", max_length=16, choices=Role.choices)
    is_active = models.BooleanField("active", default=True)
    accepted_at = models.DateTimeField("acceptée le", default=timezone.now)
    created_at = models.DateTimeField("créée le", auto_now_add=True)

    class Meta:
        ordering = ("organization__name", "user__email")
        constraints = [
            models.UniqueConstraint(
                fields=("organization", "user"), name="unique_organization_member"
            )
        ]

    def __str__(self) -> str:
        return f"{self.user.email} — {self.organization.name}"


class Invitation(models.Model):
    """Invitation privée dont seul le condensat du jeton est conservé."""

    organization = models.ForeignKey(
        Organization, on_delete=models.PROTECT, related_name="invitations"
    )
    email = models.EmailField("adresse électronique")
    role = models.CharField("rôle", max_length=16, choices=Membership.Role.choices)
    token_digest = models.CharField(max_length=64, unique=True, editable=False)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sent_invitations",
    )
    expires_at = models.DateTimeField("expire le")
    accepted_at = models.DateTimeField("acceptée le", blank=True, null=True)
    created_at = models.DateTimeField("créée le", auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("organization", "email"))]

    @property
    def is_usable(self) -> bool:
        return self.accepted_at is None and self.expires_at > timezone.now()

    def __str__(self) -> str:
        return f"Invitation {self.email} — {self.organization.name}"


class AccessRequest(models.Model):
    """Demande publique examinée avant toute création de compte."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "À examiner"
        APPROVED = "APPROVED", "Acceptée"
        REJECTED = "REJECTED", "Refusée"

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField("adresse professionnelle")
    institution = models.CharField("établissement", max_length=180)
    justification = models.TextField("motif de la demande", max_length=1200)
    status = models.CharField(
        "état", max_length=16, choices=Status.choices, default=Status.PENDING
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reviewed_access_requests",
        blank=True,
        null=True,
    )
    reviewed_at = models.DateTimeField("examinée le", blank=True, null=True)
    invitation = models.OneToOneField(
        Invitation,
        on_delete=models.PROTECT,
        related_name="access_request",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField("demandée le", auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("status", "created_at"))]

    def __str__(self) -> str:
        return f"Demande {self.email} — {self.get_status_display()}"


class AuditEvent(models.Model):
    """Trace minimale d'une action de sécurité, sans charge sensible."""

    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="audit_events",
        blank=True,
        null=True,
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="audit_events",
        blank=True,
        null=True,
    )
    action = models.CharField(max_length=80)
    target_type = models.CharField(max_length=40)
    target_id = models.CharField(max_length=64)
    outcome = models.CharField(max_length=24, default="SUCCESS")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("organization", "created_at"))]
