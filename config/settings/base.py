from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=Csv())

# Custom admin path (trailing slash required). Plain strings only — no reverse_lazy
# in settings (Vercel settings introspection JSON-encodes UNFOLD and would resolve
# reverse_lazy before apps are ready).
ADMIN_URL = config("ADMIN_URL", default="kvest-cms/")
_ADMIN_PREFIX = f"/{ADMIN_URL.strip('/')}/"


def admin_path(model_path: str) -> str:
    """Build absolute admin changelist path, e.g. admin_path('core/sitesettings/')."""
    return f"{_ADMIN_PREFIX}{model_path.lstrip('/')}"


INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django_htmx",
    "tinymce",
    "src.core",
    "src.accounts",
    "src.pages",
    "src.quest",
    "src.payments",
    "src.mailings",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "csp.middleware.CSPMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "src.core.context_processors.site_globals",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

_database_url = config("DATABASE_URL", default="")
if _database_url.startswith("postgres"):
    # postgres://user:pass@host:5432/db?sslmode=require (Neon / Vercel)
    import urllib.parse as _urlparse

    _parsed = _urlparse.urlparse(_database_url)
    _qs = _urlparse.parse_qs(_parsed.query)
    _sslmode = (_qs.get("sslmode") or ["require"])[0]
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _parsed.path.lstrip("/"),
            "USER": _urlparse.unquote(_parsed.username or ""),
            "PASSWORD": _urlparse.unquote(_parsed.password or ""),
            "HOST": _parsed.hostname,
            "PORT": _parsed.port or 5432,
            "OPTIONS": {"sslmode": _sslmode},
            "CONN_MAX_AGE": config("DB_CONN_MAX_AGE", default=0, cast=int),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "uk"
LANGUAGES = [
    ("uk", "Українська"),
    ("ru", "Русский"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Europe/Kyiv"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "accounts:cabinet"
LOGOUT_REDIRECT_URL = "pages:home"

EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@example.com")
RESEND_API_KEY = config("RESEND_API_KEY", default="")

QUEST_PRICE = config("QUEST_PRICE", default="100")
QUEST_CURRENCY = config("QUEST_CURRENCY", default="UAH")

LIQPAY_PUBLIC_KEY = config("LIQPAY_PUBLIC_KEY", default="")
LIQPAY_PRIVATE_KEY = config("LIQPAY_PRIVATE_KEY", default="")
LIQPAY_SERVER_URL = config("LIQPAY_SERVER_URL", default="")
LIQPAY_RESULT_URL = config("LIQPAY_RESULT_URL", default="")
LIQPAY_SANDBOX = config("LIQPAY_SANDBOX", default=True, cast=bool)
PAYMENTS_DEV_BYPASS = config("PAYMENTS_DEV_BYPASS", default=False, cast=bool)

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ("'self'",),
        "script-src": ("'self'",),
        "style-src": ("'self'",),
        "font-src": ("'self'", "data:"),
        "img-src": ("'self'", "data:", "blob:"),
        "media-src": ("'self'", "blob:"),
        "frame-src": ("'self'", "blob:"),
        "connect-src": ("'self'",),
        "form-action": ("'self'", "https://www.liqpay.ua"),
        "frame-ancestors": ("'none'",),
    },
    # Admin is staff-only; Unfold Alpine + TinyMCE need eval/inline.
    "EXCLUDE_URL_PREFIXES": (_ADMIN_PREFIX,),
}

TINYMCE_DEFAULT_CONFIG = {
    "height": 420,
    "menubar": False,
    "plugins": "link lists image code",
    "toolbar": "undo redo | bold italic underline | bullist numlist | link image | code",
    "content_css": False,
    "skin": "oxide",
}

UNFOLD = {
    "SITE_TITLE": "Квест-марафон",
    "SITE_HEADER": "Квест-марафон Admin",
    "SITE_SYMBOL": "extension",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Налаштування",
                "separator": True,
                "items": [
                    {
                        "title": "Налаштування сайту",
                        "icon": "settings",
                        "link": admin_path("core/sitesettings/"),
                    },
                    {
                        "title": "Статистика",
                        "icon": "bar_chart",
                        "link": admin_path("core/sitestats/"),
                    },
                ],
            },
            {
                "title": "Контент сторінок",
                "separator": True,
                "items": [],  # filled below after imports
            },
            {
                "title": "Списки контенту",
                "separator": True,
                "items": [
                    {
                        "title": "Картки «Про нас»",
                        "icon": "view_carousel",
                        "link": admin_path("pages/aboutcard/"),
                    },
                    {
                        "title": "FAQ пункти",
                        "icon": "quiz",
                        "link": admin_path("pages/faqitem/"),
                    },
                    {
                        "title": "Юридичні сторінки",
                        "icon": "gavel",
                        "link": admin_path("pages/legalpage/"),
                    },
                ],
            },
            {
                "title": "Квест",
                "separator": True,
                "items": [
                    {
                        "title": "Кімнати (ключові слова)",
                        "icon": "meeting_room",
                        "link": admin_path("quest/questroom/"),
                    },
                ],
            },
        ],
    },
}

# Lazy-fill CMS sidebar from registry (avoids circular import at module load).
def _unfold_sidebar_with_cms():
    from src.core.site_content_registry import build_content_sidebar_items

    for group in UNFOLD["SIDEBAR"]["navigation"]:
        if group.get("title") == "Контент сторінок":
            group["items"] = build_content_sidebar_items()
            break


_unfold_sidebar_with_cms()

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        "src": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}
