from django.contrib import admin
from unfold.admin import ModelAdmin

from src.accounts.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = (
        "full_name",
        "user",
        "phone",
        "payment_status",
        "current_level",
        "locale",
        "created_at",
    )
    list_filter = ("payment_status", "locale")
    search_fields = ("full_name", "phone", "user__email", "user__username")
    readonly_fields = ("consent_terms_at", "consent_age18_at", "created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        from src.core.models import SiteStats

        SiteStats.sync_from_profiles()
