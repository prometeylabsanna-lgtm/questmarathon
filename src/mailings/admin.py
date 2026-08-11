from django.contrib import admin, messages
from django.core.mail import send_mail
from django.utils import timezone
from unfold.admin import ModelAdmin

from src.mailings.models import Mailing


@admin.register(Mailing)
class MailingAdmin(ModelAdmin):
    list_display = ("subject", "recipients_count", "sent_at", "created_at")
    readonly_fields = ("sent_at", "recipients_count", "created_at")
    actions = ("send_to_all_users",)

    @admin.action(description="Надіслати всім зареєстрованим")
    def send_to_all_users(self, request, queryset):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        emails = list(
            User.objects.exclude(email="")
            .values_list("email", flat=True)
            .distinct()
        )
        for mailing in queryset:
            sent = 0
            for email in emails:
                try:
                    send_mail(
                        mailing.subject,
                        mailing.body,
                        None,
                        [email],
                        fail_silently=False,
                    )
                    sent += 1
                except Exception:
                    continue
            mailing.recipients_count = sent
            mailing.sent_at = timezone.now()
            mailing.save(update_fields=["recipients_count", "sent_at"])
        self.message_user(
            request,
            f"Розсилку запущено для {len(emails)} адрес.",
            messages.SUCCESS,
        )
