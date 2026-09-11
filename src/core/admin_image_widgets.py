"""Image preview widget + locale-aware field helpers for admin."""

from __future__ import annotations

from django.utils.html import format_html
from unfold.widgets import UnfoldAdminFileFieldWidget


class CmsImageFieldWidget(UnfoldAdminFileFieldWidget):
    """File widget with current image preview above the control."""

    def __init__(self, attrs=None):
        attrs = dict(attrs or {})
        attrs.setdefault("accept", "image/*")
        super().__init__(attrs=attrs)

    def render(self, name, value, attrs=None, renderer=None):
        widget_html = super().render(name, value, attrs, renderer)
        if not (value and getattr(value, "url", None)):
            return widget_html
        preview = format_html(
            '<div class="cms-img-preview">'
            '<img src="{}" alt="Прев’ю" width="240" height="120" '
            'style="max-height:120px;width:auto;object-fit:contain;'
            "display:block;margin-bottom:0.75rem;border-radius:0.375rem;"
            'background:#111827;padding:0.5rem;">'
            "</div>",
            value.url,
        )
        return format_html("{}{}", preview, widget_html)


class CmsRatingFileFieldWidget(UnfoldAdminFileFieldWidget):
    """Clearable file widget for PDF / PNG / JPG rating uploads."""

    def __init__(self, attrs=None):
        attrs = dict(attrs or {})
        attrs.setdefault(
            "accept",
            ".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg",
        )
        super().__init__(attrs=attrs)

    def render(self, name, value, attrs=None, renderer=None):
        widget_html = super().render(name, value, attrs, renderer)
        if value and getattr(value, "url", None):
            filename = getattr(value, "name", "") or value.url
            short = filename.rsplit("/", 1)[-1]
            hint = format_html(
                '<div class="cms-file-preview" style="margin-bottom:0.75rem;">'
                '<a href="{}" target="_blank" rel="noopener noreferrer" '
                'class="text-primary-500 underline">{}</a>'
                '<p class="text-font-subtle-light dark:text-font-subtle-dark" '
                'style="margin:0.35rem 0 0;font-size:0.85rem;">'
                "PDF, PNG, JPG, JPEG · до 10 МБ"
                "</p>"
                "</div>",
                value.url,
                short,
            )
        else:
            hint = format_html(
                '<p class="text-font-subtle-light dark:text-font-subtle-dark" '
                'style="margin:0 0 0.75rem;font-size:0.85rem;">'
                "PDF, PNG, JPG, JPEG · до 10 МБ"
                "</p>"
            )
        return format_html("{}{}", hint, widget_html)
