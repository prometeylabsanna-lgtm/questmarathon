from django.db import models


class Mailing(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sent_at = models.DateTimeField(null=True, blank=True)
    recipients_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Розсилка"
        verbose_name_plural = "Розсилки"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.subject
