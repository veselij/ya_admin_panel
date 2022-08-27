import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from split_settings.tools import include

include("components/database.py", "components/logging.py")
load_dotenv()

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "test_key")

DEBUG = os.environ.get("DEBUG", False) == "True"

ALLOWED_HOSTS = ["127.0.0.1", "b8d4-176-57-76-217.eu.ngrok.io", "localhost"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "debug_toolbar",
    "movies.apps.MoviesConfig",
    "billing.apps.BillingConfig",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = "static"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOCALE_PATH = ["movies/locale"]

# notification settings
NOTIFICATION_ENABLED = False
NOTIFICATION_TEMPLATE = "NOTIFICATION_TEMPLATE"
NOTIFICATION_NAME = "NOTIFICATION"
NOTIFICATION_QUEUE = "NOTIFICATION_QUEUE"
NOTIFICATION_HOST = os.environ.get("NOTIFICATION_HOST")

# auth settings
AUTH_ENABLED = False
AUTH_HOST = os.environ.get("AUTH_HOST", "localhost")
AUTH_PORT = int(os.environ.get("AUTH_PORT", 82))
AUTH_URL = "https://{AUTH_HOST}:{AUTH_PORT}/api/v1/user/{USER_ID}"
AUTH_URL_ROLE = "https://{AUTH_HOST}:{AUTH_PORT}/api/v1/user/{USER_ID}"

# yookassa settings
IS_FAKE_PAYMENT_API = False
WEBHOOK_API_HOST = os.environ.get("WEBHOOK_API_HOST")
WEBHOOK_API_URL = f"{WEBHOOK_API_HOST}/api/v1/billing/paymentWebhookApi"
YOOKASSA_TOKEN = os.environ.get("YOOKASSA_TOKEN")

# URL to redirect user after succefull payment
AFTER_PAYMENT_URL = "https://f4c4-176-57-76-217.eu.ngrok.io"
