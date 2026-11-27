"""Lecture stricte de la configuration injectée par l'environnement."""

import os

from django.core.exceptions import ImproperlyConfigured


def required(name: str) -> str:
    """Retourne une variable non vide ou refuse le démarrage."""
    value = os.environ.get(name, "").strip()
    if not value:
        raise ImproperlyConfigured(f"La variable {name} est obligatoire.")
    return value


def boolean(name: str, *, default: bool) -> bool:
    """Lit un booléen explicite sans conversion silencieuse."""
    value = os.environ.get(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ImproperlyConfigured(f"La variable {name} doit être un booléen.")


def integer(name: str, *, default: int, minimum: int, maximum: int) -> int:
    """Lit un entier compris dans les bornes fournies."""
    raw_value = os.environ.get(name, str(default))
    try:
        value = int(raw_value)
    except ValueError as error:
        message = f"La variable {name} doit être un entier."
        raise ImproperlyConfigured(message) from error
    if not minimum <= value <= maximum:
        raise ImproperlyConfigured(
            f"La variable {name} doit être comprise entre {minimum} et {maximum}."
        )
    return value


def csv(name: str, *, required_value: bool = False) -> list[str]:
    """Lit une liste séparée par des virgules, sans élément vide."""
    raw_value = os.environ.get(name, "")
    values = [item.strip() for item in raw_value.split(",") if item.strip()]
    if required_value and not values:
        raise ImproperlyConfigured(f"La variable {name} est obligatoire.")
    return values
