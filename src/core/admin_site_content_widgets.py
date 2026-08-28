"""Dark-readable CMS form widgets (no bg-white)."""

from __future__ import annotations

from django.contrib.admin.widgets import AdminTextareaWidget, AdminTextInputWidget
from unfold.widgets import INPUT_CLASSES, TEXTAREA_CLASSES

_SKIP_CLASSES = frozenset(
    {
        "bg-white",
        "text-font-default-light",
        "border-base-200",
        "dark:bg-base-900",
        "dark:border-base-700",
        "dark:text-font-default-dark",
    }
)
_FORCE_CLASSES = (
    "bg-base-900",
    "text-base-100",
    "border-base-700",
    "placeholder-base-400",
)


def cms_control_classes(base_classes) -> list[str]:
    classes: list[str] = []
    for item in base_classes:
        if isinstance(item, (list, tuple)):
            classes.extend(cms_control_classes(item))
            continue
        token = str(item).strip()
        if not token or token in _SKIP_CLASSES:
            continue
        classes.append(token)
    for forced in _FORCE_CLASSES:
        if forced not in classes:
            classes.append(forced)
    return classes


class CmsAdminTextInputWidget(AdminTextInputWidget):
    def __init__(self, attrs=None):
        attrs = dict(attrs or {})
        existing = attrs.get("class", "")
        merged = cms_control_classes(list(INPUT_CLASSES) + existing.split())
        attrs["class"] = " ".join(merged)
        super().__init__(attrs=attrs)


class CmsAdminTextareaWidget(AdminTextareaWidget):
    def __init__(self, attrs=None):
        attrs = dict(attrs or {})
        existing = attrs.get("class", "")
        merged = cms_control_classes(list(TEXTAREA_CLASSES) + existing.split())
        attrs["class"] = " ".join(merged)
        super().__init__(attrs=attrs)


def apply_readable_widget(widget) -> None:
    """Mutate widget.attrs for SiteSettings dark readability."""
    from django.forms.widgets import CheckboxInput, FileInput, Select

    if isinstance(widget, (CheckboxInput, Select, FileInput)):
        return
    if "TinyMCE" in type(widget).__name__:
        return
    existing = (widget.attrs.get("class") or "").split()
    widget.attrs["class"] = " ".join(cms_control_classes(existing))
