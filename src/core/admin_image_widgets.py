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
        preview = ""
        if value and getattr(value, "url", None):
            preview = format_html(
                '<div class="cms-img-preview">'
                '<img src="{}" alt="Прев’ю" width="240" height="120" '
                'style="max-height:120px;width:auto;object-fit:contain;'
                "display:block;margin-bottom:0.75rem;border-radius:0.375rem;"
                'background:#111827;padding:0.5rem;">'
                "</div>",
                value.url,
            )
        return preview + super().render(name, value, attrs, renderer)
