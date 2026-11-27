"""Services transactionnels des invitations et adhésions."""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import timedelta

from allauth.account.models import EmailAddress
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from .models import (
    AccessRequest,
    AuditEvent,
    Invitation,
    Membership,
    Organization,
    User,
)


@dataclass(frozen=True)
class IssuedInvitation:
    invitation: Invitation
    token: str


@dataclass(frozen=True)
class SubmittedAccessRequest:
    access_request: AccessRequest
    created: bool


def _digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@transaction.atomic
def submit_access_request(
    *, email: str, institution: str, justification: str
) -> SubmittedAccessRequest:
    """Enregistre une demande publique sans créer prématurément de compte."""
    normalized_email = User.objects.normalize_email(email)
    existing = (
        AccessRequest.objects.select_for_update()
        .filter(email__iexact=normalized_email, status=AccessRequest.Status.PENDING)
        .first()
    )
    if existing is not None:
        return SubmittedAccessRequest(access_request=existing, created=False)

    access_request = AccessRequest.objects.create(
        email=normalized_email,
        institution=institution.strip(),
        justification=justification.strip(),
    )
    AuditEvent.objects.create(
        action="access_request.created",
        target_type="access_request",
        target_id=str(access_request.public_id),
    )
    transaction.on_commit(
        lambda: send_mail(
            subject="Demande d’accès à AlleleFounder reçue",
            message=(
                "Votre demande d’accès a bien été reçue.\n\n"
                "Un administrateur va l’examiner. Si elle est acceptée, vous "
                "recevrez un lien personnel pour créer votre compte."
            ),
            from_email=None,
            recipient_list=[access_request.email],
        )
    )
    return SubmittedAccessRequest(access_request=access_request, created=True)


@transaction.atomic
def issue_invitation(
    *,
    organization: Organization,
    email: str,
    role: str,
    invited_by: User,
    acceptance_url: str,
) -> IssuedInvitation:
    """Crée puis envoie une invitation privée expirant après sept jours."""
    if role not in Membership.Role.values:
        raise ValueError("Le rôle demandé n'est pas reconnu.")
    normalized_email = User.objects.normalize_email(email)
    if Membership.objects.filter(
        organization=organization, user__email__iexact=normalized_email
    ).exists():
        raise ValueError("Cette personne appartient déjà à l'organisation.")
    if Invitation.objects.filter(
        organization=organization,
        email__iexact=normalized_email,
        accepted_at__isnull=True,
        expires_at__gt=timezone.now(),
    ).exists():
        raise ValueError("Une invitation active existe déjà pour cette adresse.")
    token = secrets.token_urlsafe(32)
    invitation = Invitation.objects.create(
        organization=organization,
        email=normalized_email,
        role=role,
        token_digest=_digest(token),
        invited_by=invited_by,
        expires_at=timezone.now() + timedelta(days=7),
    )
    AuditEvent.objects.create(
        organization=organization,
        actor=invited_by,
        action="invitation.created",
        target_type="invitation",
        target_id=str(invitation.pk),
    )
    transaction.on_commit(
        lambda: send_mail(
            subject="Invitation à rejoindre AlleleFounder",
            message=(
                f"Vous êtes invité à rejoindre {organization.name}.\n\n"
                f"Activez votre compte : {acceptance_url.format(token=token)}\n\n"
                "Ce lien expire dans sept jours."
            ),
            from_email=None,
            recipient_list=[invitation.email],
        )
    )
    return IssuedInvitation(invitation=invitation, token=token)


@transaction.atomic
def approve_access_request(
    *,
    access_request: AccessRequest,
    reviewed_by: User,
    acceptance_url: str,
    role: str,
    organization: Organization | None = None,
    organization_name: str = "",
) -> IssuedInvitation:
    """Accepte une demande puis envoie l'invitation de création du compte."""
    if not reviewed_by.is_staff:
        raise PermissionError("Seul un administrateur de la plateforme peut décider.")
    access_request = AccessRequest.objects.select_for_update().get(pk=access_request.pk)
    if access_request.status != AccessRequest.Status.PENDING:
        raise ValueError("Cette demande a déjà été examinée.")
    if organization is None:
        name = organization_name.strip()
        if not name:
            raise ValueError("Une organisation est requise.")
        organization = Organization.objects.create(name=name)

    issued = issue_invitation(
        organization=organization,
        email=access_request.email,
        role=role,
        invited_by=reviewed_by,
        acceptance_url=acceptance_url,
    )
    access_request.status = AccessRequest.Status.APPROVED
    access_request.reviewed_by = reviewed_by
    access_request.reviewed_at = timezone.now()
    access_request.invitation = issued.invitation
    access_request.save(
        update_fields=("status", "reviewed_by", "reviewed_at", "invitation")
    )
    AuditEvent.objects.create(
        organization=organization,
        actor=reviewed_by,
        action="access_request.approved",
        target_type="access_request",
        target_id=str(access_request.public_id),
    )
    return issued


@transaction.atomic
def reject_access_request(
    *, access_request: AccessRequest, reviewed_by: User
) -> AccessRequest:
    """Refuse une demande en informant le demandeur sans exposer de détail."""
    if not reviewed_by.is_staff:
        raise PermissionError("Seul un administrateur de la plateforme peut décider.")
    access_request = AccessRequest.objects.select_for_update().get(pk=access_request.pk)
    if access_request.status != AccessRequest.Status.PENDING:
        raise ValueError("Cette demande a déjà été examinée.")
    access_request.status = AccessRequest.Status.REJECTED
    access_request.reviewed_by = reviewed_by
    access_request.reviewed_at = timezone.now()
    access_request.save(update_fields=("status", "reviewed_by", "reviewed_at"))
    AuditEvent.objects.create(
        actor=reviewed_by,
        action="access_request.rejected",
        target_type="access_request",
        target_id=str(access_request.public_id),
    )
    transaction.on_commit(
        lambda: send_mail(
            subject="Décision concernant votre demande AlleleFounder",
            message=(
                "Votre demande d’accès ne peut pas être acceptée actuellement.\n\n"
                "Vous pouvez contacter l’administrateur de votre établissement "
                "si vous pensez qu’une information manque."
            ),
            from_email=None,
            recipient_list=[access_request.email],
        )
    )
    return access_request


def invitation_for_token(token: str) -> Invitation | None:
    """Résout une invitation par comparaison de son condensat."""
    if not token:
        return None
    return (
        Invitation.objects.select_related("organization")
        .filter(token_digest=_digest(token))
        .first()
    )


@transaction.atomic
def accept_invitation(
    *,
    invitation: Invitation,
    first_name: str = "",
    last_name: str = "",
    password: str = "",
    existing_user: User | None = None,
) -> User:
    """Active atomiquement le compte, l'adresse vérifiée et l'adhésion."""
    invitation = Invitation.objects.select_for_update().get(pk=invitation.pk)
    if not invitation.is_usable:
        raise ValueError("Cette invitation n'est plus utilisable.")

    user = User.objects.filter(email__iexact=invitation.email).first()
    if user is not None and (existing_user is None or user.pk != existing_user.pk):
        raise PermissionError(
            "Connectez-vous au compte invité avant d'accepter cette invitation."
        )
    created = user is None
    if created:
        user = User(
            email=invitation.email,
            first_name=first_name,
            last_name=last_name,
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
    assert user is not None  # nosec: établi par les deux branches précédentes.
    if (
        not created
        and Membership.objects.filter(
            user=user, organization=invitation.organization
        ).exists()
    ):
        raise ValueError("Ce compte appartient déjà à cette organisation.")

    EmailAddress.objects.update_or_create(
        user=user,
        email=invitation.email,
        defaults={"verified": True, "primary": True},
    )
    Membership.objects.create(
        user=user, organization=invitation.organization, role=invitation.role
    )
    invitation.accepted_at = timezone.now()
    invitation.save(update_fields=("accepted_at",))
    AuditEvent.objects.create(
        organization=invitation.organization,
        actor=user,
        action="invitation.accepted",
        target_type="membership",
        target_id=str(user.pk),
    )
    return user


@transaction.atomic
def change_membership_role(
    *, membership: Membership, role: str, changed_by: User
) -> Membership:
    """Change un rôle en protégeant atomiquement le dernier administrateur."""
    if role not in Membership.Role.values:
        raise ValueError("Le rôle demandé n'est pas reconnu.")
    membership = Membership.objects.select_for_update().get(pk=membership.pk)
    actor = Membership.objects.filter(
        organization=membership.organization,
        user=changed_by,
        is_active=True,
        role=Membership.Role.ADMIN,
    ).first()
    if actor is None:
        raise PermissionError("Seul un administrateur peut modifier un rôle.")
    if membership.role == Membership.Role.ADMIN and role != Membership.Role.ADMIN:
        admin_count = (
            Membership.objects.select_for_update()
            .filter(
                organization=membership.organization,
                is_active=True,
                role=Membership.Role.ADMIN,
            )
            .count()
        )
        if admin_count == 1:
            raise ValueError("Le dernier administrateur ne peut pas être rétrogradé.")
    membership.role = role
    membership.save(update_fields=("role",))
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=changed_by,
        action="membership.role_changed",
        target_type="membership",
        target_id=str(membership.pk),
    )
    return membership
