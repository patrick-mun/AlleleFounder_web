"""Réglages des tests, conservant PostgreSQL comme moteur unique."""

from .base import *  # noqa: F403

ALLOWED_HOSTS = ["testserver"]
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
STATIC_ROOT = None
STORAGES = {
    **STORAGES,  # noqa: F405
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
WHITENOISE_USE_FINDERS = True
