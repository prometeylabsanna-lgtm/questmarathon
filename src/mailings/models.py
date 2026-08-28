from django.db import models


class Mailing(models.Model):
    subject = models.CharField("Тема", max_length=255)
    body = models.TextField("Текст листа")
    sent_at = models.DateTimeField("Надіслано", null=True, blank=True)
    recipients_count = models.PositiveIntegerField("Кількість отримувачів", default=0)
    created_at = models.DateTimeField("Створено", auto_now_add=True)

    class Meta:
        verbose_name = "Розсилка"
        verbose_name_plural = "Розсилки"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.subject
