"""Adaptateurs d'authentification propres à AlleleFounder."""

import base64
import hashlib

from allauth.account.adapter import DefaultAccountAdapter
from allauth.mfa.adapter import DefaultMFAAdapter
from cryptography.fernet import Fernet
from django.conf import settings
from django.http import HttpRequest


class PrivateAccountAdapter(DefaultAccountAdapter):
    """Ferme l'inscription publique au profit des invitations contrôlées."""

    def is_open_for_signup(self, request: HttpRequest) -> bool:
        return False


class EncryptedMFAAdapter(DefaultMFAAdapter):
    """Chiffre au repos les secrets MFA gérés par django-allauth."""

    @staticmethod
    def _fernet() -> Fernet:
        encryption_secret = settings.MFA_ENCRYPTION_KEY or settings.SECRET_KEY
        digest = hashlib.sha256(encryption_secret.encode("utf-8")).digest()
        return Fernet(base64.urlsafe_b64encode(digest))

    def encrypt(self, text: str) -> str:
        return self._fernet().encrypt(text.encode("utf-8")).decode("ascii")

    def decrypt(self, encrypted_text: str) -> str:
        return self._fernet().decrypt(encrypted_text.encode("ascii")).decode("utf-8")
