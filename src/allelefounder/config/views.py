"""Vues techniques et page d'accueil du socle."""

import logging

from django.db import DatabaseError, connection
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

logger = logging.getLogger(__name__)


def home(request: HttpRequest) -> HttpResponse:
    """Affiche l'accueil public du produit."""
    return render(request, "home.html")


def permission_denied_page(request: HttpRequest) -> HttpResponse:
    """Affiche un refus sans révéler l'existence d'une ressource."""
    return render(request, "errors/403.html", status=403)


def service_unavailable(request: HttpRequest) -> HttpResponse:
    """Présente une indisponibilité contrôlée sans diagnostic sensible."""
    return render(request, "errors/503.html", status=503)


def liveness(request: HttpRequest) -> JsonResponse:
    """Confirme uniquement que le processus HTTP répond."""
    return _health_response({"status": "ok", "service": "web"})


def readiness(request: HttpRequest) -> JsonResponse:
    """Confirme que PostgreSQL accepte une requête minimale."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except DatabaseError:
        logger.warning("health.readiness.database_unavailable")
        return _health_response(
            {"status": "unavailable", "dependency": "postgresql"}, status=503
        )
    return _health_response({"status": "ok", "dependency": "postgresql"})


def _health_response(payload: dict[str, str], *, status: int = 200) -> JsonResponse:
    response = JsonResponse(payload, status=status)
    response["Cache-Control"] = "no-store"
    return response


def bad_request(request: HttpRequest, exception: Exception) -> HttpResponse:
    """Affiche une erreur 400 sans détail interne."""
    return render(request, "errors/400.html", status=400)


def permission_denied(request: HttpRequest, exception: Exception) -> HttpResponse:
    """Affiche une erreur 403 sans détail interne."""
    return render(request, "errors/403.html", status=403)


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    """Affiche une erreur 404 sans révéler la ressource demandée."""
    return render(request, "errors/404.html", status=404)


def server_error(request: HttpRequest) -> HttpResponse:
    """Affiche une erreur 500 générique."""
    return render(request, "errors/500.html", status=500)
