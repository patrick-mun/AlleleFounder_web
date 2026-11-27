"""Routes HTTP du socle AlleleFounder."""

from django.contrib import admin
from django.urls import include, path

from . import views

handler400 = "allelefounder.config.views.bad_request"
handler403 = "allelefounder.config.views.permission_denied"
handler404 = "allelefounder.config.views.page_not_found"
handler500 = "allelefounder.config.views.server_error"

urlpatterns = [
    path("", views.home, name="home"),
    path("account/", include("allauth.urls")),
    path("", include("allelefounder.accounts.urls")),
    path("permission-denied/", views.permission_denied_page, name="permission-denied"),
    path("service-unavailable/", views.service_unavailable, name="service-unavailable"),
    path("health/live/", views.liveness, name="health-live"),
    path("health/ready/", views.readiness, name="health-ready"),
    path("admin/", admin.site.urls),
]
