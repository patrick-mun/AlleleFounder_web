"""Tests des parcours visibles et de l'isolation des organisations."""

from unittest.mock import patch

from allauth.account.models import EmailAddress
from allauth.mfa.models import Authenticator
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from allelefounder.accounts.forms import InvitationAcceptanceForm
from allelefounder.accounts.models import AccessRequest, Membership, Organization, User
from allelefounder.accounts.services import issue_invitation


class AccountViewTests(TestCase):
    def _ready_user(
        self, email: str, organization: Organization, role: str
    ) -> tuple[User, Membership]:
        user = User.objects.create_user(email, "long-test-password-2026")
        EmailAddress.objects.create(
            user=user, email=user.email, verified=True, primary=True
        )
        Authenticator.objects.create(
            user=user,
            type=Authenticator.Type.TOTP,
            data={"secret": "synthetic-encrypted-secret"},
        )
        membership = Membership.objects.create(
            user=user, organization=organization, role=role
        )
        return user, membership

    def test_public_home_and_login_are_available(self) -> None:
        home = self.client.get(reverse("home"))
        login = self.client.get(reverse("account_login"))

        self.assertContains(home, "Explorer un possible effet fondateur")
        self.assertContains(home, reverse("accounts:access-request"))
        self.assertEqual(login.status_code, 200)

    def test_public_access_request_sends_receipt_without_creating_user(self) -> None:
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("accounts:access-request"),
                {
                    "email": "requester@example.test",
                    "institution": "Laboratoire Alpha",
                    "justification": (
                        "Tester le parcours avec des données synthétiques."
                    ),
                },
            )

        self.assertRedirects(response, reverse("accounts:access-requested"))
        self.assertTrue(
            AccessRequest.objects.filter(email="requester@example.test").exists()
        )
        self.assertFalse(User.objects.filter(email="requester@example.test").exists())
        self.assertEqual(len(mail.outbox), 1)

    def test_staff_can_approve_request_and_send_activation_link(self) -> None:
        staff = User.objects.create_user(
            "staff@example.test", "long-test-password-2026", is_staff=True
        )
        access_request = AccessRequest.objects.create(
            email="requester@example.test",
            institution="Laboratoire Alpha",
            justification="Tester le parcours.",
        )
        self.client.force_login(staff)
        prefix = str(access_request.public_id)

        with (
            patch(
                "allauth.account.internal.flows.reauthentication."
                "is_reauthentication_required",
                return_value=False,
            ),
            self.captureOnCommitCallbacks(execute=True),
        ):
            response = self.client.post(
                reverse(
                    "accounts:approve-access-request",
                    kwargs={"public_id": access_request.public_id},
                ),
                {
                    f"{prefix}-organization": "",
                    f"{prefix}-organization_name": "Laboratoire Alpha",
                    f"{prefix}-role": Membership.Role.ANALYST,
                },
            )

        self.assertRedirects(response, reverse("accounts:access-request-list"))
        access_request.refresh_from_db()
        self.assertEqual(access_request.status, AccessRequest.Status.APPROVED)
        self.assertIsNotNone(access_request.invitation)
        self.assertIn("/invitations/", mail.outbox[-1].body)

    def test_invited_user_can_choose_passkey_during_registration(self) -> None:
        organization = Organization.objects.create(name="Laboratoire Alpha")
        admin = User.objects.create_user(
            "admin@example.test", "long-test-password-2026"
        )
        issued = issue_invitation(
            organization=organization,
            email="passkey@example.test",
            role=Membership.Role.READER,
            invited_by=admin,
            acceptance_url="https://example.test/invitations/{token}/",
        )

        response = self.client.post(
            reverse("accounts:invitation-accept", kwargs={"token": issued.token}),
            {
                "first_name": "Alex",
                "last_name": "Martin",
                "authentication_method": (
                    InvitationAcceptanceForm.AuthenticationMethod.PASSKEY
                ),
                "password1": "",
                "password2": "",
            },
        )

        self.assertRedirects(response, reverse("mfa_add_webauthn"))
        user = User.objects.get(email="passkey@example.test")
        self.assertFalse(user.has_usable_password())
        self.assertTrue(
            EmailAddress.objects.filter(user=user, verified=True, primary=True).exists()
        )
        self.assertEqual(
            self.client.session.get("_auth_user_id"),
            str(user.pk),
        )
        passkey_page = self.client.get(reverse("mfa_add_webauthn"))
        self.assertEqual(passkey_page.status_code, 200)

    def test_dashboard_redirects_anonymous_user_to_login(self) -> None:
        response = self.client.get(reverse("accounts:dashboard"))

        self.assertRedirects(
            response,
            f"{reverse('account_login')}?next={reverse('accounts:dashboard')}",
        )

    def test_dashboard_requires_mfa(self) -> None:
        organization = Organization.objects.create(name="Laboratoire Alpha")
        user = User.objects.create_user("user@example.test", "test-password")
        EmailAddress.objects.create(
            user=user, email=user.email, verified=True, primary=True
        )
        Membership.objects.create(
            user=user, organization=organization, role=Membership.Role.READER
        )
        self.client.force_login(user)

        response = self.client.get(reverse("accounts:dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("mfa_activate_totp"))

    def test_team_is_isolated_to_active_organization(self) -> None:
        alpha = Organization.objects.create(name="Laboratoire Alpha")
        beta = Organization.objects.create(name="Laboratoire Bêta")
        user, _ = self._ready_user("reader@example.test", alpha, Membership.Role.READER)
        Membership.objects.create(
            user=user, organization=beta, role=Membership.Role.READER
        )
        beta_member, _ = self._ready_user(
            "beta@example.test", beta, Membership.Role.ANALYST
        )
        alpha_member, _ = self._ready_user(
            "alpha@example.test", alpha, Membership.Role.ANALYST
        )
        self.client.force_login(user)
        session = self.client.session
        session["active_organization"] = str(beta.public_id)
        session.save()

        response = self.client.get(reverse("accounts:team"))

        self.assertContains(response, beta_member.email)
        self.assertNotContains(response, alpha_member.email)

    def test_foreign_organization_selection_returns_not_found(self) -> None:
        alpha = Organization.objects.create(name="Laboratoire Alpha")
        beta = Organization.objects.create(name="Laboratoire Bêta")
        user, _ = self._ready_user("reader@example.test", alpha, Membership.Role.READER)
        self.client.force_login(user)

        response = self.client.post(
            reverse("accounts:organization-select"),
            {"organization": str(beta.public_id)},
        )

        self.assertEqual(response.status_code, 404)

    def test_only_administrator_can_open_invitation_page(self) -> None:
        organization = Organization.objects.create(name="Laboratoire Alpha")
        for role in Membership.Role.values:
            with self.subTest(role=role):
                user, _ = self._ready_user(
                    f"{role.lower()}@example.test", organization, role
                )
                self.client.force_login(user)
                session = self.client.session
                session["active_organization"] = str(organization.public_id)
                session.save()

                response = self.client.get(
                    reverse("accounts:invite-member"), follow=True
                )

                expected_status = 200 if role == Membership.Role.ADMIN else 403
                self.assertEqual(response.status_code, expected_status)
                self.client.logout()

    def test_administrator_can_send_invitation(self) -> None:
        organization = Organization.objects.create(name="Laboratoire Alpha")
        admin, _ = self._ready_user(
            "admin@example.test", organization, Membership.Role.ADMIN
        )
        self.client.force_login(admin)
        session = self.client.session
        session["active_organization"] = str(organization.public_id)
        session.save()

        with (
            patch(
                "allauth.account.internal.flows.reauthentication."
                "is_reauthentication_required",
                return_value=False,
            ),
            self.captureOnCommitCallbacks(execute=True),
        ):
            response = self.client.post(
                reverse("accounts:invite-member"),
                {"email": "invitee@example.test", "role": Membership.Role.ANALYST},
            )

        self.assertRedirects(response, reverse("accounts:team"))

    def test_administrator_can_change_role_in_active_organization(self) -> None:
        organization = Organization.objects.create(name="Laboratoire Alpha")
        admin, _ = self._ready_user(
            "admin@example.test", organization, Membership.Role.ADMIN
        )
        member, membership = self._ready_user(
            "member@example.test", organization, Membership.Role.READER
        )
        self.client.force_login(admin)
        session = self.client.session
        session["active_organization"] = str(organization.public_id)
        session.save()

        with patch(
            "allauth.account.internal.flows.reauthentication."
            "is_reauthentication_required",
            return_value=False,
        ):
            response = self.client.post(
                reverse(
                    "accounts:change-member-role",
                    kwargs={"public_id": membership.public_id},
                ),
                {"role": Membership.Role.REVIEWER},
            )

        self.assertRedirects(response, reverse("accounts:team"))
        membership.refresh_from_db()
        self.assertEqual(membership.role, Membership.Role.REVIEWER)
        self.assertEqual(member.email, "member@example.test")

    def test_role_change_cannot_target_another_organization(self) -> None:
        alpha = Organization.objects.create(name="Laboratoire Alpha")
        beta = Organization.objects.create(name="Laboratoire Bêta")
        admin, _ = self._ready_user("admin@example.test", alpha, Membership.Role.ADMIN)
        _, foreign_membership = self._ready_user(
            "foreign@example.test", beta, Membership.Role.READER
        )
        self.client.force_login(admin)
        session = self.client.session
        session["active_organization"] = str(alpha.public_id)
        session.save()

        with patch(
            "allauth.account.internal.flows.reauthentication."
            "is_reauthentication_required",
            return_value=False,
        ):
            response = self.client.post(
                reverse(
                    "accounts:change-member-role",
                    kwargs={"public_id": foreign_membership.public_id},
                ),
                {"role": Membership.Role.ANALYST},
            )

        self.assertEqual(response.status_code, 404)

    def test_role_change_requires_recent_reauthentication(self) -> None:
        organization = Organization.objects.create(name="Laboratoire Alpha")
        admin, _ = self._ready_user(
            "admin@example.test", organization, Membership.Role.ADMIN
        )
        _, membership = self._ready_user(
            "member@example.test", organization, Membership.Role.READER
        )
        self.client.force_login(admin)
        session = self.client.session
        session["active_organization"] = str(organization.public_id)
        session.save()

        response = self.client.post(
            reverse(
                "accounts:change-member-role",
                kwargs={"public_id": membership.public_id},
            ),
            {"role": Membership.Role.REVIEWER},
        )

        expected_path = reverse("account_reauthenticate")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(expected_path))
        membership.refresh_from_db()
        self.assertEqual(membership.role, Membership.Role.READER)

    def test_existing_account_must_log_in_before_accepting_invitation(self) -> None:
        organization = Organization.objects.create(name="Laboratoire Alpha")
        admin, _ = self._ready_user(
            "admin@example.test", organization, Membership.Role.ADMIN
        )
        existing_user = User.objects.create_user(
            "existing@example.test", "long-test-password-2026"
        )
        issued = issue_invitation(
            organization=organization,
            email=existing_user.email,
            role=Membership.Role.READER,
            invited_by=admin,
            acceptance_url="https://example.test/invitations/{token}/",
        )

        response = self.client.get(
            reverse("accounts:invitation-accept", kwargs={"token": issued.token})
        )

        expected_login = reverse("account_login")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(expected_login))

    def test_disabled_account_cannot_log_in(self) -> None:
        user = User.objects.create_user(
            "disabled@example.test", "long-test-password-2026"
        )
        user.is_active = False
        user.save(update_fields=("is_active",))

        response = self.client.post(
            reverse("account_login"),
            {
                "login": user.email,
                "password": "long-test-password-2026",
            },
        )

        self.assertRedirects(response, reverse("account_inactive"))
        self.assertNotIn("_auth_user_id", self.client.session)
