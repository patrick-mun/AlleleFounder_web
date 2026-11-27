"""Sélecteurs de lecture tenantés pour les comptes."""

from django.db.models import QuerySet

from .models import Membership, Organization, User


def active_memberships_for(user: User) -> QuerySet[Membership]:
    """Retourne uniquement les adhésions actives et organisations accessibles."""
    return Membership.objects.select_related("organization", "user").filter(
        user=user,
        is_active=True,
        organization__status=Organization.Status.ACTIVE,
    )


def membership_for_public_id(user: User, public_id: str) -> Membership | None:
    """Résout une adhésion sans révéler les organisations non accessibles."""
    return (
        active_memberships_for(user).filter(organization__public_id=public_id).first()
    )
