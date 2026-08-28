from django.contrib import admin
from tinymce.widgets import TinyMCE
from unfold.admin import ModelAdmin

from src.core.admin_filters import PublishedFilter
from src.pages.models import LegalPage


@admin.register(LegalPage)
class LegalPageAdmin(ModelAdmin):
    list_display = ("slug", "title_uk", "is_published", "updated_at")
    list_filter = (("is_published", PublishedFilter),)
    list_filter_sheet = False
    list_filter_submit = True
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

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in ("body_uk", "body_ru"):
            kwargs["widget"] = TinyMCE(attrs={"cols": 80, "rows": 30})
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    class Media:
        css = {"all": ["css/admin/site_content.css"]}
        js = ["js/admin/locale_switcher.js"]
