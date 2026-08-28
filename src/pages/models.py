from django.db import models
from django.urls import reverse


class LegalPage(models.Model):
    """Legal documents with TinyMCE HTML bodies (uk/ru share slug)."""

    slug = models.SlugField(max_length=64, unique=True)
    title_uk = models.CharField(max_length=255)
    title_ru = models.CharField(max_length=255, blank=True)
    body_uk = models.TextField(blank=True, help_text="HTML (TinyMCE)")
    body_ru = models.TextField(blank=True, help_text="HTML (TinyMCE)")
    updated_label_uk = models.CharField(max_length=255, blank=True)
    updated_label_ru = models.CharField(max_length=255, blank=True)
    is_published = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Юридична сторінка"
        verbose_name_plural = "Юридичні сторінки"
        ordering = ["slug"]

    def __str__(self) -> str:
        return f"{self.slug}: {self.title_uk}"

    def get_absolute_url(self) -> str:
        return reverse(f"pages:{self.slug}")

    def title_for(self, locale: str) -> str:
        if locale == "ru" and self.title_ru:
            return self.title_ru
        return self.title_uk

    def body_for(self, locale: str) -> str:
        if locale == "ru" and self.body_ru:
            return self.body_ru
        return self.body_uk

    def updated_label_for(self, locale: str) -> str:
        if locale == "ru" and self.updated_label_ru:
            return self.updated_label_ru
        return self.updated_label_uk


class FAQItem(models.Model):
    question_uk = models.CharField(max_length=255)
    question_ru = models.CharField(max_length=255, blank=True)
    answer_uk = models.TextField()
    answer_ru = models.TextField(blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "FAQ пункт"
        verbose_name_plural = "FAQ пункти"
        ordering = ["sort_order", "pk"]

    def __str__(self) -> str:
        return self.question_uk

    def question_for(self, locale: str) -> str:
        if locale == "ru" and self.question_ru:
            return self.question_ru
        return self.question_uk

    def answer_for(self, locale: str) -> str:
        if locale == "ru" and self.answer_ru:
            return self.answer_ru
        return self.answer_uk


class AboutCard(models.Model):
    title_uk = models.CharField(max_length=255)
    title_ru = models.CharField(max_length=255, blank=True)
    text_uk = models.TextField()
    text_ru = models.TextField(blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Картка «Про нас»"
        verbose_name_plural = "Картки «Про нас»"
        ordering = ["sort_order", "pk"]

    def __str__(self) -> str:
        return self.title_uk

    def title_for(self, locale: str) -> str:
        if locale == "ru" and self.title_ru:
            return self.title_ru
        return self.title_uk

    def text_for(self, locale: str) -> str:
        if locale == "ru" and self.text_ru:
            return self.text_ru
        return self.text_uk


class InfoPage(models.Model):
    """Legacy model — kept for data migration; prefer LegalPage / SiteBlock / FAQ."""

    class Locale(models.TextChoices):
        UK = "uk", "Українська"
        RU = "ru", "Русский"

    slug = models.SlugField(max_length=64)
    locale = models.CharField(max_length=5, choices=Locale.choices, default=Locale.UK)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Інфосторінка (legacy)"
        verbose_name_plural = "Інфосторінки (legacy)"
        unique_together = ("slug", "locale")
        ordering = ["slug", "locale"]

    def __str__(self) -> str:
        return f"{self.slug} [{self.locale}]"

    def get_absolute_url(self) -> str:
        return reverse(f"pages:{self.slug}")
