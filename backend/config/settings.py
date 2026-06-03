import os
from corsheaders.defaults import default_headers
from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

def env_list(name: str, default=None) -> list:
    value = os.getenv(name)
    if not value:
        return default or []
    return [v.strip() for v in value.split(",")]

BASE_DIR = Path(__file__).resolve().parent.parent # /backend

STORAGE_DIR_NAME = "storage"

MEDIA_URL = "/storage/"
MEDIA_ROOT = BASE_DIR / STORAGE_DIR_NAME

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles" # Для проды
STATICFILES_DIRS = [BASE_DIR / "static"]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECURITY WARNING: don't run with debug turned on in production!

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("APP_DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = env_list("APP_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env_list("APP_CSRF_TRUSTED_ORIGINS")

CORS_ALLOW_HEADERS = list(default_headers) + env_list("APP_CORS_ALLOW_HEADERS")
CORS_ALLOW_ALL_ORIGINS = os.getenv("APP_CORS_ALLOW_ALL_ORIGINS", "False").lower() == "true"
CORS_ALLOWED_ORIGINS = env_list("APP_CORS_ALLOWED_ORIGINS")
CORS_ALLOW_CREDENTIALS = True

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "drf_spectacular",
    "django_ckeditor_5",

    "apps.users",
    "apps.tournaments",
    "apps.faq",
    "apps.about_club",
    "apps.social_network",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        # "rest_framework.authentication.SessionAuthentication",
        # "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", "15"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_LIFETIME_DAYS", "7"))),
    "ROTATE_REFRESH_TOKENS": os.getenv("JWT_ROTATE_REFRESH_TOKENS", "True").lower() == "true",
    "BLACKLIST_AFTER_ROTATION": os.getenv("JWT_BLACKLIST_AFTER_ROTATION", "True").lower() == "true"
}

SPECTACULAR_SETTINGS = {
    "TITLE": os.getenv("APP_TITLE", "Title"),
    "DESCRIPTION": os.getenv("APP_DESCRIPTION"),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
    }
}

MIDDLEWARE = [
    "apps.core.middleware.DebugHeadersMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


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

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DATABASE_NAME", "app_db"),
        "USER": os.getenv("DATABASE_USER", "app_user"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD", ""),
        "HOST": os.getenv("DATABASE_HOST", "localhost"),
        "PORT": int(os.getenv("DATABASE_PORT", "5432"))
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = os.getenv("APP_DEFAULT_LANGUAGE")
TIME_ZONE = os.getenv("APP_TIME_ZONE")
USE_TZ = True
USE_I18N = True
USE_L10N = True

DATE_FORMAT = "d.m.Y"
DATETIME_FORMAT = "d.m.Y H:i"
TIME_FORMAT = "H:i"


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "1"))

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
# CELERY_RESULT_BACKEND = "redis://redis:6379/2"
CELERY_TIMEZONE = TIME_ZONE

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_BOT_ADMIN_IDS = env_list("TELEGRAM_BOT_ADMIN_IDS")

AUTH_USER_MODEL = "users.User"

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading", "|", 
            "bold", "italic", "link", "|",
            "bulletedList", "numberedList", "|",
            "blockQuote"
        ],
    }
}

APPEND_SLASH = False

LOGGER_LEVEL = os.getenv("LOGGER_LEVEL", "INFO")
LOGGER_FILE = os.getenv("LOGGER_FILE", "logs/app.log")
LOGGER_MAX_SIZE = int(os.getenv("LOGGER_MAX_SIZE", "10"))
LOGGER_BACKUP_COUNT = int(os.getenv("LOGGER_BACKUP_COUNT", "5"))

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standart": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standart",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": LOGGER_FILE,
            "maxBytes": LOGGER_MAX_SIZE * 1024 * 1024,
            "backupCount": LOGGER_BACKUP_COUNT,
            "encoding": "utf8",
        },
    },
    "loggers": {
        # DRF
        "rest_framework": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False},
        # SimpleJWT
        "rest_framework_simplejwt": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False},
        # Твой middleware / utils
        "apps.core.middleware": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False},
    },
    "root": {
        "handlers": ["console", "file"],
        "level": LOGGER_LEVEL,
    },
}

IIKO_BASE_URL = os.getenv("IIKO_BASE_URL")
IIKO_API_KEY = os.getenv("IIKO_API_KEY")
IIKO_ORGANIZATION_ID = os.getenv("IIKO_ORGANIZATION_ID")

IIKO_LOCAL_BASE_URL = os.getenv("IIKO_LOCAL_BASE_URL")
IIKO_LOCAL_LOGIN = os.getenv("IIKO_LOCAL_LOGIN")
IIKO_LOCAL_PASSWORD = os.getenv("IIKO_LOCAL_PASSWORD")
