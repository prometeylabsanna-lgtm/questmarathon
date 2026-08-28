from django.contrib import admin
from tinymce.widgets import TinyMCE
from unfold.admin import ModelAdmin

from src.pages.models import AboutCard, FAQItem, LegalPage


@admin.register(LegalPage)
class LegalPageAdmin(ModelAdmin):
    list_display = ("slug", "title_uk", "is_published", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("slug", "title_uk", "title_ru")
    prepopulated_fields = {"slug": ("title_uk",)}
    fieldsets = (
        (None, {"fields": ("slug", "is_published")}),
        ("Українська", {"fields": ("title_uk", "updated_label_uk", "body_uk")}),
        ("Російська", {"fields": ("title_ru", "updated_label_ru", "body_ru")}),
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in ("body_uk", "body_ru"):
            kwargs["widget"] = TinyMCE(attrs={"cols": 80, "rows": 30})
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(FAQItem)
class FAQItemAdmin(ModelAdmin):
    list_display = ("question_uk", "sort_order", "is_active", "updated_at")
    list_editable = ("sort_order", "is_active")
    ordering = ("sort_order", "pk")
    search_fields = ("question_uk", "question_ru", "answer_uk", "answer_ru")
    fieldsets = (
        (None, {"fields": ("sort_order", "is_active")}),
        ("Українська", {"fields": ("question_uk", "answer_uk")}),
        ("Російська", {"fields": ("question_ru", "answer_ru")}),
    )


@admin.register(AboutCard)
class AboutCardAdmin(ModelAdmin):
    list_display = ("title_uk", "sort_order", "is_active", "updated_at")
    list_editable = ("sort_order", "is_active")
    ordering = ("sort_order", "pk")
    search_fields = ("title_uk", "title_ru", "text_uk", "text_ru")
    fieldsets = (
        (None, {"fields": ("sort_order", "is_active")}),
        ("Українська", {"fields": ("title_uk", "text_uk")}),
        ("Російська", {"fields": ("title_ru", "text_ru")}),
    )
