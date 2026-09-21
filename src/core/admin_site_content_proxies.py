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
    RatingPageSettings,
    SiteFooterSettings,
    SiteHeaderSettings,
)
from src.core.site_content_registry import CONTENT_SECTIONS

SECTION_PROXY_MODELS = {
    "homeintrosettings": HomeIntroSettings,
    "siteheadersettings": SiteHeaderSettings,
    "sitefootersettings": SiteFooterSettings,
    "aboutpagesettings": AboutPageSettings,
    "faqpagesettings": FaqPageSettings,
    "contactspagesettings": ContactsPageSettings,
    "ratingpagesettings": RatingPageSettings,
}


class SingletonModelAdminMixin:
    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj, _ = self.model.objects.get_or_create(pk=1)
        return HttpResponseRedirect(
            reverse(
                f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
                args=[obj.pk],
            )
        )


class SiteContentSectionAdmin(SingletonModelAdminMixin, ModelAdmin):
    page_slug: str = ""
    section_slug: str = ""

    def change_view(self, request, object_id, form_url="", extra_context=None):
        return site_content_section_view(
            request, self.page_slug, self.section_slug, model_admin=self
        )


def register_site_content_section_admins() -> None:
    missing = [
        section.admin_model_name
        for section in CONTENT_SECTIONS
        if section.admin_model_name not in SECTION_PROXY_MODELS
    ]
    if missing:
        raise ValueError(f"No proxy model for CMS sections: {missing}")

    for section in CONTENT_SECTIONS:
        model = SECTION_PROXY_MODELS[section.admin_model_name]
        if model in admin.site._registry:
            continue

        admin_class = type(
            f"{model.__name__}Admin",
            (SiteContentSectionAdmin,),
            {"page_slug": section.page_slug, "section_slug": section.slug},
        )
        admin.site.register(model, admin_class)
