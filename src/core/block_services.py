from __future__ import annotations

from django.core.cache import cache
from django.utils.translation import get_language

from src.core.block_defaults import (
    BLOCK_CONTENT_TYPES,
    BLOCK_DEFAULTS,
    BLOCK_LABELS,
    default_for,
    is_visibility_key,
)
from src.core.models import SITE_BLOCKS_CACHE_KEY, SITE_BLOCKS_CACHE_TTL, SiteBlock


def normalize_locale(locale: str | None = None) -> str:
    code = locale or get_language() or "uk"
    return "ru" if code.startswith("ru") else "uk"


def load_site_blocks() -> dict[str, SiteBlock]:
    cached = cache.get(SITE_BLOCKS_CACHE_KEY)
    if cached is not None:
        return cached
    blocks = {b.cache_key: b for b in SiteBlock.objects.filter(is_active=True)}
    cache.set(SITE_BLOCKS_CACHE_KEY, blocks, SITE_BLOCKS_CACHE_TTL)
    return blocks


def get_block(
    page: str, key: str, site_blocks: dict[str, SiteBlock] | None = None
) -> SiteBlock | None:
    mapping = site_blocks if site_blocks is not None else load_site_blocks()
    return mapping.get(f"{page}.{key}")


def get_block_text(
    page: str,
    key: str,
    *,
    locale: str | None = None,
    site_blocks: dict[str, SiteBlock] | None = None,
    fallback: str | None = None,
) -> str:
    loc = normalize_locale(locale)
    block = get_block(page, key, site_blocks=site_blocks)
    if block is not None:
        value = block.text_for(loc)
        if value != "":
            return value
    if fallback is not None:
        return fallback
    return default_for(page, key, loc)


def is_section_visible(
    page: str,
    visibility_key: str,
    site_blocks: dict[str, SiteBlock] | None = None,
) -> bool:
    value = get_block_text(
        page, visibility_key, site_blocks=site_blocks, fallback="1"
    )
    return value not in {"0", "false", "False", ""}


def get_block_image_url(
    page: str,
    key: str,
    site_blocks: dict[str, SiteBlock] | None = None,
) -> str:
    block = get_block(page, key, site_blocks=site_blocks)
    if block and block.image:
        return block.image.url
    return ""


def get_block_file(
    page: str,
    key: str,
    site_blocks: dict[str, SiteBlock] | None = None,
) -> SiteBlock | None:
    block = get_block(page, key, site_blocks=site_blocks)
    if block and block.file:
        return block
    return None


def ensure_block(page: str, key: str) -> tuple[SiteBlock, bool]:
    defaults = BLOCK_DEFAULTS.get((page, key), {})
    ctype = BLOCK_CONTENT_TYPES.get((page, key), SiteBlock.ContentType.TEXT)
    label = BLOCK_LABELS.get((page, key), key)
    visibility_fallback = "1" if is_visibility_key(key) else ""
    return SiteBlock.objects.get_or_create(
        page=page,
        key=key,
        defaults={
            "label": label,
            "content_type": ctype,
            "text_uk": defaults.get("text_uk", visibility_fallback),
            "text_ru": defaults.get("text_ru", visibility_fallback),
        },
    )


__all__ = [
    "ensure_block",
    "get_block",
    "get_block_file",
    "get_block_image_url",
    "get_block_text",
    "is_section_visible",
    "load_site_blocks",
    "normalize_locale",
]
