from django.core.cache import cache
from django.db import models

STATS_CACHE_KEY = "core:site_stats:participants_count"
SITE_BLOCKS_CACHE_KEY = "core:site_blocks_v1"
SITE_BLOCKS_CACHE_TTL = 60
SITE_SETTINGS_CACHE_KEY = "core:site_settings_v1"


class SiteStats(models.Model):
    """Singleton denormalized counter of paid participants."""

    participants_count = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Статистика сайту"
        verbose_name_plural = "Статистика сайту"

    def __str__(self) -> str:
        return f"Paid participants: {self.participants_count}"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete(STATS_CACHE_KEY)

    @classmethod
    def get_solo(cls) -> "SiteStats":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @classmethod
    def sync_from_profiles(cls) -> int:
        from src.accounts.models import UserProfile

        count = UserProfile.objects.filter(
            payment_status=UserProfile.PaymentStatus.PAID
        ).count()
        stats = cls.get_solo()
        if stats.participants_count != count:
            stats.participants_count = count
            stats.save(update_fields=["participants_count", "updated_at"])
        return count


class SiteSettings(models.Model):
    """Singleton: branding, contacts, socials."""

    site_name = models.CharField(max_length=128, default="Квест-марафон")
    logo = models.ImageField(upload_to="branding/", blank=True)
    favicon = models.ImageField(upload_to="branding/", blank=True)
    apple_touch_icon = models.ImageField(upload_to="branding/", blank=True)
    phone = models.CharField(max_length=32, blank=True, default="+38 (093) 000-11-22")
    email = models.EmailField(blank=True, default="info@example.com")
    address_uk = models.CharField(
        max_length=255, blank=True, default="вул. Хрещатик, 1, м. Київ"
    )
    address_ru = models.CharField(
        max_length=255, blank=True, default="ул. Крещатик, 1, г. Киев"
    )
    telegram_url = models.URLField(blank=True, default="https://t.me/kvestmarafon")
    instagram_url = models.URLField(
        blank=True, default="https://www.instagram.com/kvestmarafon/"
    )
    facebook_url = models.URLField(
        blank=True, default="https://www.facebook.com/kvestmarafon"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Налаштування сайту"
        verbose_name_plural = "Налаштування сайту"

    def __str__(self) -> str:
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete(SITE_SETTINGS_CACHE_KEY)

    @classmethod
    def get_solo(cls) -> "SiteSettings":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def address_for(self, locale: str) -> str:
        if locale == "ru" and self.address_ru:
            return self.address_ru
        return self.address_uk

    def phone_href(self) -> str:
        digits = "".join(ch for ch in self.phone if ch.isdigit() or ch == "+")
        return f"tel:{digits}" if digits else ""

    def socials(self) -> list[dict[str, str]]:
        items = []
        for sid, label, url in (
            ("telegram", "Telegram", self.telegram_url),
            ("instagram", "Instagram", self.instagram_url),
            ("facebook", "Facebook", self.facebook_url),
        ):
            if url:
                items.append({"id": sid, "label": label, "href": url})
        return items


class SiteBlock(models.Model):
    """One editable slot per (page, key). Bilingual text shares the same key."""

    class Page(models.TextChoices):
        HOME = "home", "Головна"
        ABOUT = "about", "Про нас"
        FAQ = "faq", "FAQ"
        CONTACTS = "contacts", "Контакти"
        SITE = "site", "Сайт"

    class ContentType(models.TextChoices):
        TEXT = "text", "Текст"
        IMAGE = "image", "Фото"
        URL = "url", "Посилання"

    page = models.CharField(max_length=32, choices=Page.choices)
    key = models.CharField(max_length=64)
    label = models.CharField(max_length=128, blank=True)
    content_type = models.CharField(
        max_length=16, choices=ContentType.choices, default=ContentType.TEXT
    )
    text_uk = models.TextField(blank=True)
    text_ru = models.TextField(blank=True)
    image = models.ImageField(upload_to="blocks/", blank=True)
    link_url = models.CharField(max_length=512, blank=True)
    link_label = models.CharField(max_length=128, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Блок контенту"
        verbose_name_plural = "Блоки контенту"
        constraints = [
            models.UniqueConstraint(
                fields=["page", "key"], name="unique_site_block_page_key"
            ),
        ]
        ordering = ["page", "sort_order", "key"]

    def __str__(self) -> str:
        return f"{self.page}.{self.key}"

    @property
    def cache_key(self) -> str:
        return f"{self.page}.{self.key}"

    def text_for(self, locale: str) -> str:
        if locale == "ru" and self.text_ru:
            return self.text_ru
        return self.text_uk

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(SITE_BLOCKS_CACHE_KEY)


# --- CMS proxy sections (navigation slots; not separate tables) ---


class HomeIntroSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Головна — Intro"
        verbose_name_plural = "Головна — Intro"


class SiteHeaderSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Шапка"
        verbose_name_plural = "Шапка"


class SiteFooterSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Підвал"
        verbose_name_plural = "Підвал"


class AboutPageSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Про нас — заголовки"
        verbose_name_plural = "Про нас — заголовки"


class FaqPageSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "FAQ — заголовки"
        verbose_name_plural = "FAQ — заголовки"


class ContactsPageSettings(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = "Контакти — тексти"
        verbose_name_plural = "Контакти — тексти"
