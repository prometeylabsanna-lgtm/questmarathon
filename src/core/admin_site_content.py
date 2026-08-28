"""Dynamic CMS section form + change view for SiteBlock proxies."""

from __future__ import annotations

from django import forms
from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from unfold.widgets import UnfoldAdminFileFieldWidget, UnfoldBooleanWidget

from src.core.admin_site_content_widgets import (
    CmsAdminTextareaWidget,
    CmsAdminTextInputWidget,
)
from src.core.block_defaults import (
    BLOCK_CONTENT_TYPES,
    BLOCK_DEFAULTS,
    BLOCK_LABELS,
    INLINE_KEYS,
    MULTILINE_KEYS,
    is_visibility_key,
)
from src.core.models import SITE_BLOCKS_CACHE_KEY, SiteBlock, SiteSettings
from src.core.site_content_registry import get_section


def ensure_block(page: str, key: str) -> SiteBlock:
    defaults = BLOCK_DEFAULTS.get((page, key), {})
    ctype = BLOCK_CONTENT_TYPES.get((page, key), SiteBlock.ContentType.TEXT)
    label = BLOCK_LABELS.get((page, key), key)
    obj, _ = SiteBlock.objects.get_or_create(
        page=page,
        key=key,
        defaults={
            "label": label,
            "content_type": ctype,
            "text_uk": defaults.get("text_uk", "1" if is_visibility_key(key) else ""),
            "text_ru": defaults.get("text_ru", "1" if is_visibility_key(key) else ""),
        },
    )
    return obj


def load_section_blocks(page_slug: str, section_slug: str) -> dict[str, SiteBlock]:
    section = get_section(page_slug, section_slug)
    if section is None:
        return {}
    result: dict[str, SiteBlock] = {}
    for page, key in section.blocks:
        result[key] = ensure_block(page, key)
    return result


class SitePageContentForm(forms.Form):
    def __init__(self, *args, page_slug: str, section_slug: str, **kwargs):
        self.page_slug = page_slug
        self.section_slug = section_slug
        self.section = get_section(page_slug, section_slug)
        self.blocks = load_section_blocks(page_slug, section_slug)
        super().__init__(*args, **kwargs)
        if self.section is None:
            return
        if self.section.visibility_key:
            block = self.blocks[self.section.visibility_key]
            self.fields["section_visible"] = forms.BooleanField(
                required=False,
                initial=block.text_uk != "0",
                label="Показувати секцію на сайті",
                widget=UnfoldBooleanWidget,
            )
        for page, key in self.section.blocks:
            if key == self.section.visibility_key:
                continue
            block = self.blocks[key]
            label = block.label or BLOCK_LABELS.get((page, key), key)
            ctype = BLOCK_CONTENT_TYPES.get((page, key), block.content_type)
            if is_visibility_key(key):
                self.fields[f"block__{page}__{key}__visible"] = forms.BooleanField(
                    required=False,
                    initial=block.text_uk != "0",
                    label=label,
                    widget=UnfoldBooleanWidget,
                )
                continue
            if ctype == SiteBlock.ContentType.IMAGE or ctype == "image":
                self.fields[f"block__{page}__{key}__image"] = forms.ImageField(
                    required=False,
                    label=label,
                    widget=UnfoldAdminFileFieldWidget,
                )
                continue
            if key in INLINE_KEYS:
                widget_uk = CmsAdminTextInputWidget()
                widget_ru = CmsAdminTextInputWidget()
            elif key in MULTILINE_KEYS:
                widget_uk = CmsAdminTextareaWidget(attrs={"rows": 4})
                widget_ru = CmsAdminTextareaWidget(attrs={"rows": 4})
            else:
                widget_uk = CmsAdminTextareaWidget(attrs={"rows": 2})
                widget_ru = CmsAdminTextareaWidget(attrs={"rows": 2})
            self.fields[f"block__{page}__{key}__text_uk"] = forms.CharField(
                required=False,
                initial=block.text_uk,
                label=f"{label} (UK)",
                widget=widget_uk,
            )
            self.fields[f"block__{page}__{key}__text_ru"] = forms.CharField(
                required=False,
                initial=block.text_ru,
                label=f"{label} (RU)",
                widget=widget_ru,
            )

    def save(self) -> None:
        if self.section is None:
            return
        cleaned = self.cleaned_data
        if self.section.visibility_key:
            block = self.blocks[self.section.visibility_key]
            flag = "1" if cleaned.get("section_visible") else "0"
            block.text_uk = flag
            block.text_ru = flag
            block.save(update_fields=["text_uk", "text_ru", "updated_at"])
        for page, key in self.section.blocks:
            if key == self.section.visibility_key:
                continue
            block = self.blocks[key]
            ctype = BLOCK_CONTENT_TYPES.get((page, key), block.content_type)
            if is_visibility_key(key):
                flag = "1" if cleaned.get(f"block__{page}__{key}__visible") else "0"
                block.text_uk = flag
                block.text_ru = flag
                block.save(update_fields=["text_uk", "text_ru", "updated_at"])
                continue
            if ctype == "image" or ctype == SiteBlock.ContentType.IMAGE:
                image = cleaned.get(f"block__{page}__{key}__image")
                if image:
                    block.image = image
                    block.content_type = SiteBlock.ContentType.IMAGE
                    block.save(update_fields=["image", "content_type", "updated_at"])
                continue
            uk = cleaned.get(f"block__{page}__{key}__text_uk", "")
            ru = cleaned.get(f"block__{page}__{key}__text_ru", "")
            block.text_uk = uk
            block.text_ru = ru
            block.save(update_fields=["text_uk", "text_ru", "updated_at"])
        cache.delete(SITE_BLOCKS_CACHE_KEY)


def _grouped_fields(form: SitePageContentForm) -> list[dict]:
    if form.section is None:
        return []
    groups: list[dict] = []
    if "section_visible" in form.fields:
        groups.append(
            {
                "title": "Видимість",
                "fields": [form["section_visible"]],
            }
        )
    used: set[str] = set()
    for group in form.section.field_groups:
        fields = []
        for key in group.keys:
            page = form.section.page_slug
            for suffix in ("visible", "image", "text_uk", "text_ru"):
                name = f"block__{page}__{key}__{suffix}"
                if name in form.fields:
                    fields.append(form[name])
                    used.add(name)
        if fields:
            groups.append({"title": group.title, "fields": fields})
    orphans = [form[name] for name in form.fields if name not in used and name != "section_visible"]
    if orphans:
        groups.append({"title": "Інше", "fields": orphans})
    return groups


def site_content_section_view(request, page_slug: str, section_slug: str, model_admin):
    section = get_section(page_slug, section_slug)
    SiteSettings.get_solo()
    if section is None:
        messages.error(request, "Секцію не знайдено в registry.")
        return HttpResponseRedirect(reverse("admin:index"))

    if request.method == "POST":
        form = SitePageContentForm(
            request.POST, request.FILES, page_slug=page_slug, section_slug=section_slug
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Збережено.")
            return HttpResponseRedirect(request.path)
    else:
        form = SitePageContentForm(page_slug=page_slug, section_slug=section_slug)

    context = {
        **model_admin.admin_site.each_context(request),
        "title": section.title,
        "section": section,
        "form": form,
        "field_groups": _grouped_fields(form),
        "opts": model_admin.model._meta,
        "has_view_permission": True,
        "has_change_permission": model_admin.has_change_permission(request),
        "media": form.media,
    }
    return render(request, "admin/core/site_content_page.html", context)
