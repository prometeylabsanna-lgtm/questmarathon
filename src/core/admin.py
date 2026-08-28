from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from src.core.admin_site_content_proxies import register_site_content_section_admins
from src.core.admin_site_content_widgets import apply_readable_widget
from src.core.models import SiteSettings, SiteStats


class ReadableUnfoldFieldsMixin:
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if formfield is not None and hasattr(formfield, "widget"):
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
            {"fields": ("site_name", "logo", "favicon", "apple_touch_icon", "logo_preview")},
        ),
        (
            "Контакти",
            {"fields": ("phone", "email", "address_uk", "address_ru")},
        ),
        (
            "Соцмережі",
            {"fields": ("telegram_url", "instagram_url", "facebook_url")},
        ),
    )
    readonly_fields = ("logo_preview",)

    @admin.display(description="Прев’ю логотипу")
    def logo_preview(self, obj):
        if obj and obj.logo:
            return format_html(
                '<img src="{}" alt="" style="max-height:80px;width:auto;">',
                obj.logo.url,
            )
        return "—"


register_site_content_section_admins()
