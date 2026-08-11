from django.contrib import admin
from unfold.admin import ModelAdmin

from src.quest.models import QuestRoom


@admin.register(QuestRoom)
class QuestRoomAdmin(ModelAdmin):
    list_display = ("order", "title_uk", "media_type", "is_active", "updated_at")
    list_editable = ("is_active",)
    ordering = ("order",)
    search_fields = ("title_uk", "title_ru", "keyword_normalized")
