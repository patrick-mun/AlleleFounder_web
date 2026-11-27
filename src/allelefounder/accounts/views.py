"""Vues minces des comptes et organisations."""

from allauth.account.decorators import reauthentication_required
from allauth.account.internal.flows.login import record_authentication
from allauth.account.models import EmailAddress
from allauth.mfa.utils import is_mfa_enabled
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .access import app_access_required
from .forms import (
    AccessApprovalForm,
    AccessRequestForm,
    InvitationAcceptanceForm,
    InvitationForm,
    MembershipRoleForm,
)
from .models import AccessRequest, Invitation, Membership, User
from .selectors import active_memberships_for, membership_for_public_id
from .services import (
    accept_invitation,
    approve_access_request,
    change_membership_role,
    invitation_for_token,
    issue_invitation,
    reject_access_request,
    submit_access_request,
)


def request_access(request: HttpRequest) -> HttpResponse:
    """Collecte une demande publique sans créer de compte ni d'adhésion."""
    form = AccessRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        submit_access_request(
            email=form.cleaned_data["email"],
            institution=form.cleaned_data["institution"],
            justification=form.cleaned_data["justification"],
        )
        return redirect("accounts:access-requested")
    return render(request, "accounts/access_request.html", {"form": form})


def access_requested(request: HttpRequest) -> HttpResponse:
    """Confirme la réception sans révéler si l'adresse était déjà connue."""
    return render(request, "accounts/access_requested.html")


@staff_member_required(login_url="account_login")
def access_request_list(request: HttpRequest) -> HttpResponse:
    """Présente les demandes en attente aux administrateurs de plateforme."""
    pending_requests = AccessRequest.objects.filter(status=AccessRequest.Status.PENDING)
    request_cards = [
        {
            "access_request": item,
            "form": AccessApprovalForm(
                prefix=str(item.public_id),
                initial={
                    "organization_name": item.institution,
                    "role": Membership.Role.READER,
                },
            ),
        }
        for item in pending_requests
    ]
    return render(
        request,
        "accounts/access_request_list.html",
        {"request_cards": request_cards},
    )


@staff_member_required(login_url="account_login")
@reauthentication_required(app="allelefounder.access_requests")
def approve_access_request_view(request: HttpRequest, public_id: str) -> HttpResponse:
    """Décide une demande et déclenche l'e-mail d'activation."""
    if request.method != "POST":
        raise Http404
    access_request = get_object_or_404(
        AccessRequest,
        public_id=public_id,
        status=AccessRequest.Status.PENDING,
    )
    form = AccessApprovalForm(request.POST, prefix=str(public_id))
    if form.is_valid():
        token_marker = "INVITATION_TOKEN"
        path = reverse("accounts:invitation-accept", kwargs={"token": token_marker})
        url_template = request.build_absolute_uri(path).replace(token_marker, "{token}")
        try:
            approve_access_request(
                access_request=access_request,
                reviewed_by=request.user,
                acceptance_url=url_template,
                role=form.cleaned_data["role"],
                organization=form.cleaned_data["organization"],
                organization_name=form.cleaned_data["organization_name"],
            )
        except ValueError as error:
            messages.error(request, str(error))
        else:
            messages.success(request, "La demande est acceptée et le lien envoyé.")
    else:
        messages.error(request, "La décision est incomplète.")
    return redirect("accounts:access-request-list")


@staff_member_required(login_url="account_login")
@reauthentication_required(app="allelefounder.access_requests")
def reject_access_request_view(request: HttpRequest, public_id: str) -> HttpResponse:
    """Refuse une demande en conservant une décision auditée."""
    if request.method != "POST":
        raise Http404
    access_request = get_object_or_404(
        AccessRequest,
        public_id=public_id,
        status=AccessRequest.Status.PENDING,
    )
    try:
        reject_access_request(access_request=access_request, reviewed_by=request.user)
    except ValueError as error:
        messages.error(request, str(error))
    else:
        messages.success(request, "La demande a été refusée et la personne informée.")
    return redirect("accounts:access-request-list")


def invitation_accept(request: HttpRequest, token: str) -> HttpResponse:
    """Affiche puis accepte une invitation opaque encore valide."""
    invitation = invitation_for_token(token)
    if invitation is None or not invitation.is_usable:
        raise Http404

    existing_user = User.objects.filter(email__iexact=invitation.email).first()
    if existing_user is not None and not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())
    if existing_user is not None and request.user.pk != existing_user.pk:
        raise PermissionDenied

    if existing_user is not None and request.method == "POST":
        user = accept_invitation(
            invitation=invitation,
            existing_user=existing_user,
        )
        return _complete_invitation(request, invitation, user)

    form = InvitationAcceptanceForm(request.POST or None)
    if existing_user is None and request.method == "POST" and form.is_valid():
        candidate = User(
            email=invitation.email,
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
        )
        if form.validate_for_user(candidate):
            try:
                user = accept_invitation(
                    invitation=invitation,
                    first_name=form.cleaned_data["first_name"],
                    last_name=form.cleaned_data["last_name"],
                    password=(
                        form.cleaned_data["password1"]
                        if form.cleaned_data["authentication_method"]
                        == InvitationAcceptanceForm.AuthenticationMethod.PASSWORD_TOTP
                        else ""
                    ),
                )
            except ValueError as error:
                form.add_error(None, str(error))
            else:
                return _complete_invitation(
                    request,
                    invitation,
                    user,
                    authentication_method=form.cleaned_data["authentication_method"],
                )

    return render(
        request,
        "accounts/invitation_accept.html",
        {
            "existing_account": existing_user is not None,
            "form": form,
            "invitation": invitation,
        },
    )


def _complete_invitation(
    request: HttpRequest,
    invitation: Invitation,
    user: User,
    authentication_method: str = "",
) -> HttpResponse:
    if not request.user.is_authenticated:
        login(
            request,
            user,
            backend="allauth.account.auth_backends.AuthenticationBackend",
        )
        record_authentication(
            request,
            user,
            method="code",
            reauthenticated=True,
        )
    request.session["active_organization"] = str(invitation.organization.public_id)
    if is_mfa_enabled(user):
        messages.success(request, "L'organisation a été ajoutée à votre compte.")
        return redirect("accounts:dashboard")
    if authentication_method == InvitationAcceptanceForm.AuthenticationMethod.PASSKEY:
        messages.success(
            request,
            "Votre adresse est validée. Enregistrez maintenant votre clé d’accès.",
        )
        return redirect("mfa_add_webauthn")
    messages.success(
        request,
        "Votre compte est activé. Configurez maintenant la double vérification.",
    )
    return redirect("mfa_activate_totp")


@login_required
def organization_select(request: HttpRequest) -> HttpResponse:
    """Sélectionne côté serveur une organisation accessible au compte."""
    if not _identity_is_ready(request):
        return redirect("mfa_activate_totp")
    memberships = active_memberships_for(request.user)
    if request.method == "POST":
        membership = membership_for_public_id(
            request.user, request.POST.get("organization", "")
        )
        if membership is None:
            raise Http404
        request.session["active_organization"] = str(membership.organization.public_id)
        return redirect("accounts:dashboard")
    return render(
        request,
        "accounts/organization_select.html",
        {"memberships": memberships},
    )


@app_access_required()
def dashboard(request: HttpRequest) -> HttpResponse:
    """Affiche le tableau de bord vide du lot 2."""
    return render(request, "accounts/dashboard.html", _app_context(request))


@app_access_required()
def profile(request: HttpRequest) -> HttpResponse:
    """Affiche le profil et les accès de sécurité disponibles."""
    context = _app_context(request)
    context["memberships"] = active_memberships_for(request.user)
    return render(request, "accounts/profile.html", context)


@app_access_required()
def team(request: HttpRequest) -> HttpResponse:
    """Liste les membres de l'organisation active sans fuite inter-tenant."""
    context = _app_context(request)
    context["team_memberships"] = Membership.objects.select_related("user").filter(
        organization=request.organization,
        is_active=True,  # type: ignore[attr-defined]
    )
    context["pending_invitations"] = request.organization.invitations.filter(  # type: ignore[attr-defined]
        accepted_at__isnull=True
    )
    context["role_choices"] = Membership.Role.choices
    return render(request, "accounts/team.html", context)


@app_access_required(roles=(Membership.Role.ADMIN,))
@reauthentication_required(allow_get=True, app="allelefounder.accounts")
def invite_member(request: HttpRequest) -> HttpResponse:
    """Crée une invitation pour l'organisation active de l'administrateur."""
    form = InvitationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        token_marker = "INVITATION_TOKEN"
        path = reverse("accounts:invitation-accept", kwargs={"token": token_marker})
        url_template = request.build_absolute_uri(path).replace(token_marker, "{token}")
        try:
            issue_invitation(
                organization=request.organization,  # type: ignore[attr-defined]
                email=form.cleaned_data["email"],
                role=form.cleaned_data["role"],
                invited_by=request.user,
                acceptance_url=url_template,
            )
        except ValueError as error:
            form.add_error("email", str(error))
        else:
            messages.success(request, "L'invitation a été envoyée.")
            return redirect("accounts:team")
    return render(
        request,
        "accounts/invite_member.html",
        {**_app_context(request), "form": form},
    )


@app_access_required(roles=(Membership.Role.ADMIN,))
@reauthentication_required(app="allelefounder.accounts")
def change_member_role(request: HttpRequest, public_id: str) -> HttpResponse:
    """Modifie un rôle uniquement dans l'organisation active."""
    if request.method != "POST":
        raise Http404
    membership = Membership.objects.filter(
        organization=request.organization,  # type: ignore[attr-defined]
        public_id=public_id,
        is_active=True,
    ).first()
    if membership is None:
        raise Http404
    form = MembershipRoleForm(request.POST)
    if form.is_valid():
        try:
            change_membership_role(
                membership=membership,
                role=form.cleaned_data["role"],
                changed_by=request.user,
            )
        except ValueError as error:
            messages.error(request, str(error))
        else:
            messages.success(request, "Le rôle a été mis à jour.")
    return redirect("accounts:team")


@login_required
def no_membership(request: HttpRequest) -> HttpResponse:
    """Explique l'absence d'organisation sans exposer de détail interne."""
    return render(request, "accounts/no_membership.html", status=403)


def _identity_is_ready(request: HttpRequest) -> bool:
    return EmailAddress.objects.filter(
        user=request.user, email=request.user.email, verified=True
    ).exists() and is_mfa_enabled(request.user)


def _app_context(request: HttpRequest) -> dict[str, object]:
    return {
        "organization": request.organization,  # type: ignore[attr-defined]
        "membership": request.membership,  # type: ignore[attr-defined]
    }
