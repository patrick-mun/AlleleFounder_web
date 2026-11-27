"""Contexte technique associé à chaque requête HTTP."""

from collections.abc import Callable
from uuid import UUID, uuid4

from django.http import HttpRequest, HttpResponse

from .logging import request_id_context


class RequestIdMiddleware:
    """Associe un identifiant UUID contrôlé à la requête et à sa réponse."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request_id = self._request_id(request.headers.get("X-Request-ID"))
        token = request_id_context.set(request_id)
        request.request_id = request_id
        try:
            response = self.get_response(request)
            response["X-Request-ID"] = request_id
            return response
        finally:
            request_id_context.reset(token)

    @staticmethod
    def _request_id(candidate: str | None) -> str:
        if not candidate:
            return str(uuid4())
        try:
            return str(UUID(candidate))
        except (ValueError, AttributeError):
            return str(uuid4())
