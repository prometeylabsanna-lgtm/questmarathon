from decouple import Csv, config

from .base import *  # noqa: F403

DEBUG = False

SECRET_KEY = config("SECRET_KEY")

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", cast=Csv())

PAYMENTS_DEV_BYPASS = False

EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="src.mailings.backends.ResendEmailBackend",
)
