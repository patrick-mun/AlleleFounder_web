#!/usr/bin/env python3
"""Point d'entrée des commandes d'administration Django."""

import os
import sys


def main() -> None:
    """Exécute une commande Django avec les réglages locaux par défaut."""
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "allelefounder.config.settings.local"
    )

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
