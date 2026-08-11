from django.contrib import admin
from unfold.admin import ModelAdmin

from src.pages.models import InfoPage


@admin.register(InfoPage)
class InfoPageAdmin(ModelAdmin):
    list_display = ("slug", "locale", "title", "is_published", "updated_at")
    list_filter = ("locale", "is_published", "slug")
    search_fields = ("title", "body", "slug")
