"""Réglages communs, sans valeur de repli pour les secrets ou PostgreSQL."""

from pathlib import Path

from allelefounder.config.environment import integer, required

SRC_DIR = Path(__file__).resolve().parents[3]
BASE_DIR = SRC_DIR.parent

SECRET_KEY = required("DJANGO_SECRET_KEY")
DEBUG = False
ALLOWED_HOSTS: list[str] = []

INSTALLED_APPS = [
    "django.contrib.humanize",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "allauth",
    "allauth.account",
    "allauth.mfa",
    "allauth.usersessions",
    "allelefounder.accounts.apps.AccountsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "allelefounder.common.middleware.RequestIdMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "allelefounder.config.urls"
WSGI_APPLICATION = "allelefounder.config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [SRC_DIR / "allelefounder" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": required("POSTGRES_DB"),
        "USER": required("POSTGRES_USER"),
        "PASSWORD": required("POSTGRES_PASSWORD"),
        "HOST": required("POSTGRES_HOST"),
        "PORT": integer("POSTGRES_PORT", default=5432, minimum=1, maximum=65535),
        "CONN_MAX_AGE": integer(
            "POSTGRES_CONN_MAX_AGE", default=60, minimum=0, maximum=3600
        ),
        "CONN_HEALTH_CHECKS": True,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        )
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "accounts.User"
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
ACCOUNT_ADAPTER = "allelefounder.accounts.adapters.PrivateAccountAdapter"
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_CONFIRM_EMAIL_ON_GET = False
ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_LOGIN_TIMEOUT = 900
ACCOUNT_SESSION_REMEMBER = False
MFA_SUPPORTED_TYPES = ["totp", "webauthn", "recovery_codes"]
MFA_ADAPTER = "allelefounder.accounts.adapters.EncryptedMFAAdapter"
MFA_PASSKEY_LOGIN_ENABLED = True
MFA_WEBAUTHN_USER_VERIFICATION = "required"
MFA_RECOVERY_CODES_SHOW_ONCE = True
MFA_TOTP_ISSUER = "AlleleFounder"
MFA_ENCRYPTION_KEY = None
USERSESSIONS_TRACK_ACTIVITY = False
LOGIN_REDIRECT_URL = "accounts:dashboard"
LOGIN_URL = "account_login"
ACCOUNT_LOGOUT_REDIRECT_URL = "home"
DEFAULT_FROM_EMAIL = "AlleleFounder <noreply@allelefounder.invalid>"
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [SRC_DIR / "allelefounder" / "static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "safe_json": {"()": "allelefounder.common.logging.SafeJsonFormatter"}
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "safe_json"}
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django.server": {"handlers": ["console"], "level": "INFO", "propagate": False}
    },
}
