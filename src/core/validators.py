"""Shared upload validators for CMS media."""

from __future__ import annotations

from pathlib import Path

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

RATING_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
RATING_FILE_EXTENSIONS = frozenset({".pdf", ".png", ".jpg", ".jpeg"})
RATING_IMAGE_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg"})


def rating_file_kind(name: str) -> str:
    ext = Path(name or "").suffix.lower()
    if ext == ".pdf":
        return "pdf"
    if ext in RATING_IMAGE_EXTENSIONS:
        return "image"
    return ""


def validate_rating_file(uploaded) -> None:
    if not uploaded:
        return
    name = getattr(uploaded, "name", "") or ""
    ext = Path(name).suffix.lower()
    if ext not in RATING_FILE_EXTENSIONS:
        raise ValidationError(
            _("Дозволені формати: PDF, PNG, JPG, JPEG."),
            code="invalid_extension",
        )
    size = getattr(uploaded, "size", None)
    if size is not None and size > RATING_FILE_MAX_BYTES:
        raise ValidationError(
            _("Розмір файлу не може перевищувати 10 МБ."),
            code="file_too_large",
        )
