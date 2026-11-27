"""Formulaires des parcours d'organisation et d'invitation."""

from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.db import models

from .models import AccessRequest, Membership, Organization


class AccessRequestForm(forms.ModelForm):
    """Collecte uniquement les éléments nécessaires à la décision d'accès."""

    class Meta:
        model = AccessRequest
        fields = ("email", "institution", "justification")
        widgets = {
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "institution": forms.TextInput(attrs={"autocomplete": "organization"}),
            "justification": forms.Textarea(attrs={"rows": 5}),
        }


class AccessApprovalForm(forms.Form):
    organization = forms.ModelChoiceField(
        label="Organisation existante",
        queryset=Organization.objects.none(),
        required=False,
        empty_label="Créer une nouvelle organisation",
    )
    organization_name = forms.CharField(
        label="Nom de la nouvelle organisation",
        max_length=180,
        required=False,
    )
    role = forms.ChoiceField(
        label="Rôle initial",
        choices=Membership.Role.choices,
        initial=Membership.Role.READER,
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["organization"].queryset = Organization.objects.filter(
            status=Organization.Status.ACTIVE
        )

    def clean(self) -> dict[str, object]:
        cleaned_data = super().clean()
        if not cleaned_data.get("organization") and not cleaned_data.get(
            "organization_name"
        ):
            self.add_error(
                "organization_name",
                "Sélectionnez une organisation ou indiquez-en une nouvelle.",
            )
        return cleaned_data


class InvitationForm(forms.Form):
    email = forms.EmailField(label="Adresse professionnelle")
    role = forms.ChoiceField(label="Rôle", choices=Membership.Role.choices)


class MembershipRoleForm(forms.Form):
    role = forms.ChoiceField(label="Nouveau rôle", choices=Membership.Role.choices)


class InvitationAcceptanceForm(forms.Form):
    class AuthenticationMethod(models.TextChoices):
        PASSKEY = "PASSKEY", "Clé d’accès — recommandée"
        PASSWORD_TOTP = "PASSWORD_TOTP", "Mot de passe et application de codes"

    first_name = forms.CharField(label="Prénom", max_length=150)
    last_name = forms.CharField(label="Nom", max_length=150)
    authentication_method = forms.ChoiceField(
        label="Méthode de connexion",
        choices=AuthenticationMethod.choices,
        widget=forms.RadioSelect,
        initial=AuthenticationMethod.PASSKEY,
    )
    password1 = forms.CharField(
        label="Mot de passe — uniquement pour l’option avec application de codes",
        strip=False,
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Confirmation du mot de passe",
        strip=False,
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def clean(self) -> dict[str, object]:
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        uses_password = (
            cleaned_data.get("authentication_method")
            == self.AuthenticationMethod.PASSWORD_TOTP
        )
        if uses_password and not password1:
            self.add_error("password1", "Un mot de passe est requis pour cette option.")
        if uses_password and not password2:
            self.add_error("password2", "Confirmez le mot de passe.")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Les deux mots de passe diffèrent.")
        return cleaned_data

    def validate_for_user(self, user) -> bool:
        if (
            self.cleaned_data.get("authentication_method")
            != self.AuthenticationMethod.PASSWORD_TOTP
        ):
            return not self.errors
        password = self.cleaned_data.get("password2")
        if password:
            try:
                password_validation.validate_password(password, user)
            except ValidationError as error:
                self.add_error("password2", error)
        return not self.errors
