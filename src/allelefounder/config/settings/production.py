"""Réglages durcis destinés au déploiement institutionnel."""

from django.core.exceptions import ImproperlyConfigured

from allelefounder.config.environment import csv, integer, required

from .base import *  # noqa: F403

ALLOWED_HOSTS = csv("DJANGO_ALLOWED_HOSTS", required_value=True)
if "*" in ALLOWED_HOSTS:
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS ne peut pas contenir '*'.")

CSRF_TRUSTED_ORIGINS = csv("DJANGO_CSRF_TRUSTED_ORIGINS", required_value=True)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Strict"
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = required("DJANGO_EMAIL_HOST")
EMAIL_PORT = integer("DJANGO_EMAIL_PORT", default=587, minimum=1, maximum=65535)
EMAIL_HOST_USER = required("DJANGO_EMAIL_USER")
EMAIL_HOST_PASSWORD = required("DJANGO_EMAIL_PASSWORD")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = required("DJANGO_DEFAULT_FROM_EMAIL")
MFA_ENCRYPTION_KEY = required("DJANGO_MFA_ENCRYPTION_KEY")
