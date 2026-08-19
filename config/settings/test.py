import os

os.environ.setdefault("SECRET_KEY", "django-test-secret-key")

from .develop import *  # noqa: F403

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

PAYMENTS_DEV_BYPASS = True
