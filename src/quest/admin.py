from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display

from src.quest.models import QuestRoom


@admin.register(QuestRoom)
class QuestRoomAdmin(ModelAdmin):
    list_display = (
        "order",
        "title_uk",
        "keyword_badge",
        "media_type",
        "is_active",
        "updated_at",
    )
    list_editable = ("is_active",)
    ordering = ("order",)
    search_fields = ("title_uk", "title_ru", "keyword_normalized")
    list_filter = ("media_type", "is_active")
    fieldsets = (
        (
            "Порядок і статус",
            {"fields": ("order", "is_active")},
        ),
        (
            "Ключове слово",
            {
                "fields": ("keyword_normalized",),
                "description": (
                    "Одне слово для uk і ru. При збереженні нормалізується "
                    "(trim + casefold). Регістр і зайві пробіли на фронті не важливі."
                ),
            },
        ),
        (
            "Українська",
            {"fields": ("title_uk", "body_uk")},
        ),
        (
            "Російська",
            {"fields": ("title_ru", "body_ru")},
        ),
        (
            "Медіа",
            {"fields": ("media_file", "media_type")},
        ),
    )

    @display(description="Ключ", label=True)
    def keyword_badge(self, obj):
        return obj.keyword_normalized or "—"
