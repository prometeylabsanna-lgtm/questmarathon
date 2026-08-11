from django.conf import settings
from django.db import models


class Payment(models.Model):
    class Status(models.TextChoices):
        CREATED = "created", "Створено"
        PENDING = "pending", "Очікує"
        SUCCESS = "success", "Успішно"
        FAILURE = "failure", "Помилка"
        SANDBOX = "sandbox", "Sandbox / bypass"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    provider = models.CharField(max_length=32, default="liqpay")
    order_id = models.CharField(max_length=64, unique=True)
    external_id = models.CharField(max_length=128, blank=True, db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=8, default="UAH")
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.CREATED,
        db_index=True,
    )
    idempotency_key = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        unique=True,
    )
    raw_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Платіж"
        verbose_name_plural = "Платежі"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.order_id} [{self.status}]"
