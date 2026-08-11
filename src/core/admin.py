from django.contrib import admin
from unfold.admin import ModelAdmin

from src.core.models import SiteStats


@admin.register(SiteStats)
class SiteStatsAdmin(ModelAdmin):
    list_display = ("participants_count", "updated_at")
    readonly_fields = ("participants_count", "updated_at")

    def has_add_permission(self, request):
        return not SiteStats.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
