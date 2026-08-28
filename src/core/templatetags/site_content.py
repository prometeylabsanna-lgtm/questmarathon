from __future__ import annotations

from django import template
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.html import escape
from django.utils.safestring import mark_safe

from src.core.block_services import (
    get_block_image_url,
    get_block_text,
    is_section_visible,
    load_site_blocks,
    normalize_locale,
)

register = template.Library()


def _blocks_from_context(context):
    return context.get("site_blocks") or load_site_blocks()


@register.simple_tag(takes_context=True)
def block_plain(context, page: str, key: str, fallback: str = "") -> str:
    locale = normalize_locale(context.get("LANGUAGE_CODE"))
    text = get_block_text(
        page,
        key,
        locale=locale,
        site_blocks=_blocks_from_context(context),
        fallback=fallback or None,
    )
    return text


@register.simple_tag(takes_context=True)
def section_visible(context, page: str, visibility_key: str) -> bool:
    return is_section_visible(
        page, visibility_key, site_blocks=_blocks_from_context(context)
    )


@register.simple_tag(takes_context=True)
def block_image(
    context,
    page: str,
    key: str,
    css_class: str = "",
    fallback_static: str = "",
    alt: str = "",
    width: str = "",
    height: str = "",
) -> str:
    url = get_block_image_url(page, key, site_blocks=_blocks_from_context(context))
    if not url and fallback_static:
        url = staticfiles_storage.url(fallback_static)
    if not url:
        return ""
    attrs = [f'src="{escape(url)}"', f'alt="{escape(alt)}"']
    if css_class:
        attrs.append(f'class="{escape(css_class)}"')
    if width:
        attrs.append(f'width="{escape(width)}"')
    if height:
        attrs.append(f'height="{escape(height)}"')
    attrs.append('decoding="async"')
    return mark_safe(f"<img {' '.join(attrs)}>")


@register.simple_tag(takes_context=True)
def block_html(context, page: str, key: str, fallback: str = ""):
    """Trusted staff HTML from SiteBlock (use sparingly)."""
    text = block_plain(context, page, key, fallback=fallback)
    return mark_safe(text)
