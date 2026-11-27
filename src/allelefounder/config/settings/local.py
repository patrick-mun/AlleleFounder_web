"""Réglages du développement local, toujours adossé à PostgreSQL."""

from allelefounder.config.environment import boolean, csv

from .base import *  # noqa: F403

DEBUG = boolean("DJANGO_DEBUG", default=True)
ALLOWED_HOSTS = csv("DJANGO_ALLOWED_HOSTS") or ["localhost", "127.0.0.1"]
