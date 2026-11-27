"""Tests des services tenantés du lot 2."""

from datetime import timedelta

from allauth.account.models import EmailAddress
from django.core import mail
from django.test import TestCase
from django.utils import timezone

from allelefounder.accounts.adapters import EncryptedMFAAdapter
from allelefounder.accounts.models import (
    AccessRequest,
    Invitation,
    Membership,
    Organization,
    User,
)
from allelefounder.accounts.services import (
    accept_invitation,
    approve_access_request,
    change_membership_role,
    issue_invitation,
    reject_access_request,
    submit_access_request,
)


class AccessRequestServiceTests(TestCase):
    def setUp(self) -> None:
        self.staff = User.objects.create_user(
            "staff@example.test", "test-password", is_staff=True
        )

    def test_submission_sends_receipt_without_creating_account(self) -> None:
        with self.captureOnCommitCallbacks(execute=True):
            submitted = submit_access_request(
                email="Researcher@EXAMPLE.TEST",
                institution="Laboratoire Alpha",
                justification="Évaluer l’outil avec des données synthétiques.",
            )

        self.assertTrue(submitted.created)
        self.assertEqual(submitted.access_request.email, "Researcher@example.test")
        self.assertFalse(User.objects.filter(email__iexact="researcher@example.test"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("bien été reçue", mail.outbox[0].body)

    def test_duplicate_pending_submission_is_idempotent(self) -> None:
        first = submit_access_request(
            email="researcher@example.test",
            institution="Laboratoire Alpha",
            justification="Premier motif",
        )

        second = submit_access_request(
            email="RESEARCHER@example.test",
            institution="Laboratoire Bêta",
            justification="Second motif",
        )

        self.assertEqual(first.access_request, second.access_request)
        self.assertFalse(second.created)
        self.assertEqual(
            AccessRequest.objects.filter(status=AccessRequest.Status.PENDING).count(),
            1,
        )

    def test_approval_creates_organization_and_sends_activation_link(self) -> None:
        submitted = submit_access_request(
            email="researcher@example.test",
            institution="Laboratoire Alpha",
            justification="Évaluer le parcours.",
        )

        with self.captureOnCommitCallbacks(execute=True):
            issued = approve_access_request(
                access_request=submitted.access_request,
                reviewed_by=self.staff,
                acceptance_url="https://example.test/invitations/{token}/",
                role=Membership.Role.ANALYST,
                organization_name="Laboratoire Alpha",
            )

        submitted.access_request.refresh_from_db()
        self.assertEqual(submitted.access_request.status, AccessRequest.Status.APPROVED)
        self.assertEqual(submitted.access_request.invitation, issued.invitation)
        self.assertTrue(Organization.objects.filter(name="Laboratoire Alpha").exists())
        self.assertIn(issued.token, mail.outbox[-1].body)

    def test_rejection_is_audited_and_notified(self) -> None:
        submitted = submit_access_request(
            email="researcher@example.test",
            institution="Laboratoire Alpha",
            justification="Évaluer le parcours.",
        )

        with self.captureOnCommitCallbacks(execute=True):
            reject_access_request(
                access_request=submitted.access_request,
                reviewed_by=self.staff,
            )

        submitted.access_request.refresh_from_db()
        self.assertEqual(submitted.access_request.status, AccessRequest.Status.REJECTED)
        self.assertIn("ne peut pas être acceptée", mail.outbox[-1].body)


class InvitationServiceTests(TestCase):
    def setUp(self) -> None:
        self.admin = User.objects.create_user("admin@example.test", "test-password")
        self.organization = Organization.objects.create(name="Laboratoire Alpha")
        Membership.objects.create(
            user=self.admin,
            organization=self.organization,
            role=Membership.Role.ADMIN,
        )

    def test_issue_invitation_stores_only_digest_and_sends_after_commit(self) -> None:
        with self.captureOnCommitCallbacks(execute=True):
            issued = issue_invitation(
                organization=self.organization,
                email="Analyste@EXAMPLE.TEST",
                role=Membership.Role.ANALYST,
                invited_by=self.admin,
                acceptance_url="https://example.test/invitations/{token}/",
            )

        self.assertEqual(issued.invitation.email, "Analyste@example.test")
        self.assertNotIn(issued.token, issued.invitation.token_digest)
        self.assertEqual(len(issued.invitation.token_digest), 64)
        self.assertIn(issued.token, mail.outbox[0].body)

    def test_duplicate_active_invitation_is_refused(self) -> None:
        issue_invitation(
            organization=self.organization,
            email="analyste@example.test",
            role=Membership.Role.ANALYST,
            invited_by=self.admin,
            acceptance_url="https://example.test/invitations/{token}/",
        )

        with self.assertRaisesRegex(ValueError, "invitation active"):
            issue_invitation(
                organization=self.organization,
                email="ANALYSTE@example.test",
                role=Membership.Role.READER,
                invited_by=self.admin,
                acceptance_url="https://example.test/invitations/{token}/",
            )

    def test_accept_invitation_creates_verified_user_and_membership(self) -> None:
        issued = issue_invitation(
            organization=self.organization,
            email="new@example.test",
            role=Membership.Role.REVIEWER,
            invited_by=self.admin,
            acceptance_url="https://example.test/invitations/{token}/",
        )

        user = accept_invitation(
            invitation=issued.invitation,
            first_name="Camille",
            last_name="Martin",
            password="long-test-password-2026",
        )

        self.assertTrue(user.check_password("long-test-password-2026"))
        self.assertTrue(
            EmailAddress.objects.filter(user=user, verified=True, primary=True).exists()
        )
        self.assertTrue(
            Membership.objects.filter(
                user=user,
                organization=self.organization,
                role=Membership.Role.REVIEWER,
            ).exists()
        )

    def test_passkey_registration_creates_account_without_known_password(self) -> None:
        issued = issue_invitation(
            organization=self.organization,
            email="passkey@example.test",
            role=Membership.Role.READER,
            invited_by=self.admin,
            acceptance_url="https://example.test/invitations/{token}/",
        )

        user = accept_invitation(
            invitation=issued.invitation,
            first_name="Alex",
            last_name="Martin",
        )

        self.assertFalse(user.has_usable_password())
        self.assertTrue(
            EmailAddress.objects.filter(user=user, verified=True, primary=True).exists()
        )

    def test_expired_invitation_is_refused(self) -> None:
        invitation = Invitation.objects.create(
            organization=self.organization,
            email="expired@example.test",
            role=Membership.Role.READER,
            token_digest="a" * 64,
            invited_by=self.admin,
            expires_at=timezone.now() - timedelta(minutes=1),
        )

        with self.assertRaisesRegex(ValueError, "plus utilisable"):
            accept_invitation(
                invitation=invitation,
                first_name="Test",
                last_name="Expiré",
                password="long-test-password-2026",
            )

    def test_existing_account_requires_proven_identity(self) -> None:
        existing_user = User.objects.create_user(
            "existing@example.test", "long-test-password-2026"
        )
        issued = issue_invitation(
            organization=self.organization,
            email=existing_user.email,
            role=Membership.Role.READER,
            invited_by=self.admin,
            acceptance_url="https://example.test/invitations/{token}/",
        )

        with self.assertRaises(PermissionError):
            accept_invitation(invitation=issued.invitation)

    def test_authenticated_existing_account_can_join_another_organization(
        self,
    ) -> None:
        existing_user = User.objects.create_user(
            "existing@example.test", "long-test-password-2026"
        )
        issued = issue_invitation(
            organization=self.organization,
            email=existing_user.email,
            role=Membership.Role.READER,
            invited_by=self.admin,
            acceptance_url="https://example.test/invitations/{token}/",
        )

        accepted_user = accept_invitation(
            invitation=issued.invitation,
            existing_user=existing_user,
        )

        self.assertEqual(accepted_user, existing_user)
        self.assertTrue(
            Membership.objects.filter(
                user=existing_user,
                organization=self.organization,
                role=Membership.Role.READER,
            ).exists()
        )


class MFAAdapterTests(TestCase):
    def test_secret_is_encrypted_and_can_be_decrypted(self) -> None:
        adapter = EncryptedMFAAdapter()

        encrypted = adapter.encrypt("synthetic-totp-secret")

        self.assertNotIn("synthetic-totp-secret", encrypted)
        self.assertEqual(adapter.decrypt(encrypted), "synthetic-totp-secret")


class MembershipRoleServiceTests(TestCase):
    def setUp(self) -> None:
        self.organization = Organization.objects.create(name="Laboratoire Alpha")
        self.admin = User.objects.create_user("admin@example.test", "test-password")
        self.admin_membership = Membership.objects.create(
            user=self.admin,
            organization=self.organization,
            role=Membership.Role.ADMIN,
        )

    def test_last_administrator_cannot_be_demoted(self) -> None:
        with self.assertRaisesRegex(ValueError, "dernier administrateur"):
            change_membership_role(
                membership=self.admin_membership,
                role=Membership.Role.READER,
                changed_by=self.admin,
            )

    def test_non_administrator_cannot_change_role(self) -> None:
        reader = User.objects.create_user("reader@example.test", "test-password")
        reader_membership = Membership.objects.create(
            user=reader,
            organization=self.organization,
            role=Membership.Role.READER,
        )

        with self.assertRaises(PermissionError):
            change_membership_role(
                membership=self.admin_membership,
                role=Membership.Role.ANALYST,
                changed_by=reader_membership.user,
            )
