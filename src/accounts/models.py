from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    class PaymentStatus(models.TextChoices):
        UNPAID = "unpaid", "Не оплачено"
        PENDING = "pending", "Очікує"
        PAID = "paid", "Оплачено"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    full_name = models.CharField("Ім'я", max_length=150)
    phone = models.CharField("Телефон", max_length=32)
    payment_status = models.CharField(
        max_length=16,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID,
        db_index=True,
    )
    current_level = models.PositiveSmallIntegerField(default=0)
    locale = models.CharField(max_length=5, default="uk")
    consent_terms_at = models.DateTimeField(null=True, blank=True)
    consent_age18_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Профіль гравця"
        verbose_name_plural = "Гравці"

    def __str__(self) -> str:
        return f"{self.full_name} <{self.user.email}>"

    @classmethod
    def for_user(cls, user) -> "UserProfile":
        profile, _created = cls.objects.get_or_create(
            user=user,
            defaults={"full_name": user.get_username(), "phone": ""},
        )
        return profile

    @property
    def is_paid(self) -> bool:
        return self.payment_status == self.PaymentStatus.PAID

    def mark_paid(self) -> None:
        if self.payment_status == self.PaymentStatus.PAID:
            return
        self.payment_status = self.PaymentStatus.PAID
        self.save(update_fields=["payment_status", "updated_at"])
        from src.core.models import SiteStats

        SiteStats.sync_from_profiles()
