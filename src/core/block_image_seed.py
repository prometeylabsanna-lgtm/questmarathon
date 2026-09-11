"""Seed SiteBlock.image from static fallbacks (idempotent, no overwrite)."""

from __future__ import annotations

from pathlib import Path

from django.contrib.staticfiles.finders import find
from django.core.files import File

from src.core.block_defaults import BLOCK_IMAGE_FALLBACKS, BLOCK_LABELS
from src.core.models import SiteBlock


def seed_block_fallback_images() -> int:
    """Copy static fallbacks into SiteBlock.image when the field is empty."""
    seeded = 0
    for (page, key), static_rel in BLOCK_IMAGE_FALLBACKS.items():
        if seed_one_block_image(page, key):
            seeded += 1
    return seeded


def seed_one_block_image(page: str, key: str) -> bool:
    """Seed one block image from BLOCK_IMAGE_FALLBACKS. Returns True if written."""
    static_rel = BLOCK_IMAGE_FALLBACKS.get((page, key))
    if not static_rel:
        return False
    block, _ = SiteBlock.objects.get_or_create(
        page=page,
        key=key,
        defaults={
            "label": BLOCK_LABELS.get((page, key), key),
            "content_type": SiteBlock.ContentType.IMAGE,
        },
    )
    if block.image:
        return False
    abs_path = find(static_rel)
    if not abs_path:
        return False
    filename = Path(static_rel).name
    with open(abs_path, "rb") as fh:
        block.image.save(filename, File(fh), save=False)
    block.content_type = SiteBlock.ContentType.IMAGE
    block.save(update_fields=["image", "content_type", "updated_at"])
    return True
