from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from unfold.admin import ModelAdmin

from src.core.admin_image_widgets import CmsImageFieldWidget
from src.core.admin_site_content_proxies import register_site_content_section_admins
from src.core.admin_site_content_widgets import apply_readable_widget
from src.core.models import SiteSettings, SiteStats


class ReadableUnfoldFieldsMixin:
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.get_internal_type() == "ImageField":
            kwargs.setdefault("widget", CmsImageFieldWidget)
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if (
            formfield is not None
            and hasattr(formfield, "widget")
            and db_field.get_internal_type() != "ImageField"
        ):
            apply_readable_widget(formfield.widget)
        return formfield


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


@admin.register(SiteStats)
class SiteStatsAdmin(ModelAdmin):
    list_display = ("participants_count", "updated_at")
    readonly_fields = ("participants_count", "updated_at")

    def has_add_permission(self, request):
        return not SiteStats.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteSettings)
class SiteSettingsAdmin(ReadableUnfoldFieldsMixin, SingletonModelAdminMixin, ModelAdmin):
    fieldsets = (
        (
            "Бренд",
            {
                "classes": ["tab"],
                "fields": ("site_name", "logo", "favicon", "apple_touch_icon"),
            },
        ),
        (
            "Контакти",
            {
                "classes": ["tab"],
                "fields": (
                    "phone",
                    "email",
                    "telegram_url",
                    "instagram_url",
                    "facebook_url",
                ),
            },
        ),
        (
            "Українська",
            {"classes": ["tab"], "fields": ("address_uk",)},
        ),
        (
            "Російська",
            {"classes": ["tab"], "fields": ("address_ru",)},
        ),
    )

    class Media:
        css = {"all": ["css/admin/site_content.css"]}
        js = ["js/admin/locale_switcher.js", "js/admin/collection_formset.js"]


register_site_content_section_admins()
