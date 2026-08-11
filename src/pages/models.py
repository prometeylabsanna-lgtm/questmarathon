from django.db import models
from django.urls import reverse


class InfoPage(models.Model):
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
        verbose_name = "Інфосторінка"
        verbose_name_plural = "Інфосторінки"
        unique_together = ("slug", "locale")
        ordering = ["slug", "locale"]

    def __str__(self) -> str:
        return f"{self.slug} [{self.locale}]"

    def get_absolute_url(self) -> str:
        return reverse(f"pages:{self.slug}")
