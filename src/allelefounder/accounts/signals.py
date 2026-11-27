"""Traduction des signaux d'authentification en événements d'audit sûrs."""

from allauth.mfa import signals as mfa_signals
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver

from .models import AuditEvent, User


@receiver(user_logged_in)
def audit_login(sender, request, user: User, **kwargs) -> None:
    AuditEvent.objects.create(
        actor=user,
        action="account.login",
        target_type="user",
        target_id=str(user.pk),
    )


@receiver(user_login_failed)
def audit_login_failure(sender, credentials, request, **kwargs) -> None:
    AuditEvent.objects.create(
        action="account.login_failed",
        target_type="user",
        target_id="unknown",
        outcome="DENIED",
    )


def _audit_authenticator(action: str, user: User, authenticator) -> None:
    AuditEvent.objects.create(
        actor=user,
        action=action,
        target_type="authenticator",
        target_id=str(authenticator.pk),
    )


@receiver(mfa_signals.authenticator_added)
def audit_authenticator_added(sender, request, user, authenticator, **kwargs) -> None:
    _audit_authenticator("mfa.authenticator_added", user, authenticator)


@receiver(mfa_signals.authenticator_removed)
def audit_authenticator_removed(sender, request, user, authenticator, **kwargs) -> None:
    _audit_authenticator("mfa.authenticator_removed", user, authenticator)


@receiver(mfa_signals.authenticator_reset)
def audit_authenticator_reset(sender, request, user, authenticator, **kwargs) -> None:
    _audit_authenticator("mfa.authenticator_reset", user, authenticator)


@receiver(mfa_signals.authentication_failed)
def audit_mfa_failure(sender, request, user, authenticator, **kwargs) -> None:
    AuditEvent.objects.create(
        actor=user,
        action="mfa.authentication_failed",
        target_type="authenticator",
        target_id=str(getattr(authenticator, "pk", "unknown")),
        outcome="DENIED",
    )
