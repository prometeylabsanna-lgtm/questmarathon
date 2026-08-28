"""Register proxy ModelAdmins for each CMS ContentSection."""

from __future__ import annotations

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from unfold.admin import ModelAdmin

from src.core.admin_site_content import site_content_section_view
from src.core.models import (
    AboutPageSettings,
    ContactsPageSettings,
    FaqPageSettings,
    HomeIntroSettings,
    SiteFooterSettings,
    SiteHeaderSettings,
    SiteSettings,
)

_SECTION_MODELS = (
    (HomeIntroSettings, "home", "intro"),
    (SiteHeaderSettings, "site", "header"),
    (SiteFooterSettings, "site", "footer"),
    (AboutPageSettings, "about", "main"),
    (FaqPageSettings, "faq", "main"),
    (ContactsPageSettings, "contacts", "main"),
)


class SingletonSettingsAdmin(ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj, _ = SiteSettings.objects.get_or_create(pk=1)
        return HttpResponseRedirect(
            reverse(
                f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
                args=[obj.pk],
            )
        )


class SiteContentSectionAdmin(SingletonSettingsAdmin):
    page_slug: str = ""
    section_slug: str = ""

    def change_view(self, request, object_id, form_url="", extra_context=None):
        return site_content_section_view(
            request, self.page_slug, self.section_slug, model_admin=self
        )


def register_site_content_section_admins() -> None:
    for model, page_slug, section_slug in _SECTION_MODELS:
        if model in admin.site._registry:
            continue

        admin_class = type(
            f"{model.__name__}Admin",
            (SiteContentSectionAdmin,),
            {"page_slug": page_slug, "section_slug": section_slug},
        )
        admin.site.register(model, admin_class)
