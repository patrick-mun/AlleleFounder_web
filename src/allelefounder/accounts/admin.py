"""Administration des comptes."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import (
    AccessRequest,
    AuditEvent,
    Invitation,
    Membership,
    Organization,
    User,
)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Présente l'utilisateur personnalisé dans l'administration Django."""

    ordering = ("email",)
    list_display = ("email", "is_staff", "is_active")
    search_fields = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Informations personnelles",
            {"fields": ("first_name", "last_name")},
        ),
        (
            "Autorisations",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "public_id")
    list_filter = ("status",)
    search_fields = ("name",)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "organization", "role", "is_active", "public_id")
    list_filter = ("role", "is_active", "organization")
    search_fields = ("user__email", "organization__name")


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ("email", "organization", "role", "expires_at", "accepted_at")
    list_filter = ("role", "organization")
    search_fields = ("email",)
    readonly_fields = ("token_digest", "created_at", "accepted_at")


@admin.register(AccessRequest)
class AccessRequestAdmin(admin.ModelAdmin):
    list_display = ("email", "institution", "status", "created_at", "reviewed_at")
    list_filter = ("status", "institution")
    search_fields = ("email", "institution")
    readonly_fields = (
        "public_id",
        "email",
        "institution",
        "justification",
        "status",
        "reviewed_by",
        "reviewed_at",
        "invitation",
        "created_at",
    )

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("created_at", "action", "organization", "actor", "outcome")
    list_filter = ("action", "outcome", "organization")
    readonly_fields = (
        "organization",
        "actor",
        "action",
        "target_type",
        "target_id",
        "outcome",
        "created_at",
    )

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False
