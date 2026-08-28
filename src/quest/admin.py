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
            {"classes": ["tab"], "fields": ("order", "is_active")},
        ),
        (
            "Ключове слово",
            {
                "classes": ["tab"],
                "fields": ("keyword_normalized",),
                "description": (
                    "Одне слово для української та російської версій. "
                    "При збереженні нормалізується (пробіли + регістр)."
                ),
            },
        ),
        (
            "Українська",
            {"classes": ["tab"], "fields": ("title_uk", "body_uk")},
        ),
        (
            "Російська",
            {"classes": ["tab"], "fields": ("title_ru", "body_ru")},
        ),
        (
            "Медіа",
            {"classes": ["tab"], "fields": ("media_file", "media_type")},
        ),
    )

    @display(description="Ключове слово", label=True)
    def keyword_badge(self, obj):
        return obj.keyword_normalized or "—"

    class Media:
        css = {"all": ["css/admin/site_content.css"]}
        js = ["js/admin/locale_switcher.js"]
