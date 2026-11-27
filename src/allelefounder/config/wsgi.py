"""Point d'entrée WSGI de production."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "allelefounder.config.settings.production"
)

application = get_wsgi_application()
