"""Décorateurs d'accès au cadre applicatif authentifié."""

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

from allauth.account.models import EmailAddress
from allauth.mfa.utils import is_mfa_enabled
from django.contrib.auth.views import redirect_to_login
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from .models import Membership
from .selectors import active_memberships_for, membership_for_public_id

View = TypeVar("View", bound=Callable[..., HttpResponse])


def app_access_required(*, roles: tuple[str, ...] = ()) -> Callable[[View], View]:
    """Exige compte vérifié, MFA et adhésion dans l'organisation active."""

    def decorator(view: View) -> View:
        @wraps(view)
        def wrapped(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if not EmailAddress.objects.filter(
                user=request.user, email=request.user.email, verified=True
            ).exists():
                return redirect("account_email_verification_sent")
            if not is_mfa_enabled(request.user):
                return redirect("mfa_activate_totp")

            membership = _active_membership(request)
            if membership is None:
                memberships = active_memberships_for(request.user)
                if not memberships.exists():
                    return redirect("accounts:no-membership")
                if memberships.count() == 1:
                    membership = memberships.get()
                    request.session["active_organization"] = str(
                        membership.organization.public_id
                    )
                else:
                    return redirect("accounts:organization-select")
            if roles and membership.role not in roles:
                return redirect("permission-denied")

            request.organization = membership.organization  # type: ignore[attr-defined]
            request.membership = membership  # type: ignore[attr-defined]
            return view(request, *args, **kwargs)

        return cast(View, wrapped)

    return decorator


def _active_membership(request: HttpRequest) -> Membership | None:
    public_id = request.session.get("active_organization")
    if not public_id:
        return None
    return membership_for_public_id(request.user, public_id)
