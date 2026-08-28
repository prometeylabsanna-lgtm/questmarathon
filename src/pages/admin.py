from django.contrib import admin
from tinymce.widgets import TinyMCE
from unfold.admin import ModelAdmin

from src.pages.models import LegalPage


@admin.register(LegalPage)
class LegalPageAdmin(ModelAdmin):
    list_display = ("slug", "title_uk", "is_published_ua", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("slug", "title_uk", "title_ru")
    prepopulated_fields = {"slug": ("title_uk",)}
    fieldsets = (
        (
            "Загальне",
            {"classes": ["tab"], "fields": ("slug", "is_published")},
        ),
        (
            "Українська",
            {
                "classes": ["tab"],
                "fields": ("title_uk", "updated_label_uk", "body_uk"),
            },
        ),
        (
            "Російська",
            {
                "classes": ["tab"],
                "fields": ("title_ru", "updated_label_ru", "body_ru"),
            },
        ),
    )

    @admin.display(description="Опубліковано", boolean=True)
    def is_published_ua(self, obj):
        return obj.is_published

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in ("body_uk", "body_ru"):
            kwargs["widget"] = TinyMCE(attrs={"cols": 80, "rows": 30})
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        labels = {
            "slug": "URL-slug",
            "is_published": "Опубліковано",
            "title_uk": "Заголовок",
            "title_ru": "Заголовок",
            "updated_label_uk": "Мітка оновлення",
            "updated_label_ru": "Мітка оновлення",
            "body_uk": "Текст (HTML)",
            "body_ru": "Текст (HTML)",
        }
        if formfield is not None and db_field.name in labels:
            formfield.label = labels[db_field.name]
        return formfield

    class Media:
        css = {"all": ["css/admin/site_content.css"]}
        js = ["js/admin/locale_switcher.js"]
