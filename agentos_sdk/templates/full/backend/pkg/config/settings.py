import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

def env_bool(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}

def env_list(name: str, default: list) -> list:
    raw_value = os.getenv(name, "")
    values = [item.strip() for item in raw_value.split(",") if item.strip()]
    return values or list(default)

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-template-secret-key")
DEBUG = env_bool("DEBUG", True)
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", ["localhost", "127.0.0.1", "backend"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "__PKG__.accounts",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "__PKG__.config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "__PKG__.config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "/data/db.sqlite3" if os.path.exists("/data") else BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

# CORS and CSRF Settings
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    ["http://localhost:3001", "http://127.0.0.1:3001"]
)
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    ["http://localhost:3001", "http://127.0.0.1:3001"]
)

# AgentOS SSO variables
AGENTOS_URL = os.getenv("AGENTOS_URL", "http://host.docker.internal:8088")
AGENTOS_KEY = os.getenv("AGENTOS_KEY", "")
AGENTOS_OIDC_ISSUER = os.getenv("AGENTOS_OIDC_ISSUER", "http://host.docker.internal:8088")
AGENTOS_OIDC_PUBLIC_ISSUER = os.getenv("AGENTOS_OIDC_PUBLIC_ISSUER", "http://localhost:8088")
AGENTOS_CLIENT_ID = os.getenv("AGENTOS_CLIENT_ID", "")
AGENTOS_CLIENT_SECRET = os.getenv("AGENTOS_CLIENT_SECRET", "")
AGENTOS_REDIRECT_URI = os.getenv("AGENTOS_REDIRECT_URI", "http://localhost:3001/api/auth/agentos/callback/")
AGENTOS_LOGIN_REDIRECT = os.getenv("AGENTOS_LOGIN_REDIRECT", "/")

# Cookies setup for local http development (non-secure Lax cookies)
SESSION_COOKIE_NAME = "__PKG___sessionid"
CSRF_COOKIE_NAME = "__PKG___csrftoken"
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "__PKG__.accounts.auth.CsrfExemptSessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
