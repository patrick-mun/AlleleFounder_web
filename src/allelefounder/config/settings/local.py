"""Réglages du développement local, toujours adossé à PostgreSQL."""

import os

from allelefounder.config.environment import boolean, csv, integer

from .base import *  # noqa: F403

DEBUG = boolean("DJANGO_DEBUG", default=True)
ALLOWED_HOSTS = csv("DJANGO_ALLOWED_HOSTS") or ["localhost", "127.0.0.1"]
EMAIL_HOST = os.environ.get("DJANGO_EMAIL_HOST", "")
EMAIL_PORT = integer("DJANGO_EMAIL_PORT", default=1025, minimum=1, maximum=65535)
EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
    if EMAIL_HOST
    else "django.core.mail.backends.console.EmailBackend"
)
EMAIL_USE_TLS = False
MFA_WEBAUTHN_ALLOW_INSECURE_ORIGIN = True
