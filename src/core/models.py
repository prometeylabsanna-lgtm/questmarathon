from django.core.cache import cache
from django.db import models

STATS_CACHE_KEY = "core:site_stats:participants_count"


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
