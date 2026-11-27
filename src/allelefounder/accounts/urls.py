"""Routes des comptes et organisations AlleleFounder."""

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("demande-acces/", views.request_access, name="access-request"),
    path("demande-acces/recue/", views.access_requested, name="access-requested"),
    path(
        "administration/demandes-acces/",
        views.access_request_list,
        name="access-request-list",
    ),
    path(
        "administration/demandes-acces/<uuid:public_id>/accepter/",
        views.approve_access_request_view,
        name="approve-access-request",
    ),
    path(
        "administration/demandes-acces/<uuid:public_id>/refuser/",
        views.reject_access_request_view,
        name="reject-access-request",
    ),
    path("app/", views.dashboard, name="dashboard"),
    path("app/organizations/", views.organization_select, name="organization-select"),
    path("app/team/", views.team, name="team"),
    path("app/team/invite/", views.invite_member, name="invite-member"),
    path(
        "app/team/members/<uuid:public_id>/role/",
        views.change_member_role,
        name="change-member-role",
    ),
    path("app/account/", views.profile, name="profile"),
    path("app/no-membership/", views.no_membership, name="no-membership"),
    path("invitations/<str:token>/", views.invitation_accept, name="invitation-accept"),
]
