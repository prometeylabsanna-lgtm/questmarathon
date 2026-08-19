from django.contrib import admin
from unfold.admin import ModelAdmin

from src.payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = (
        "order_id",
        "user",
        "amount",
        "currency",
        "status",
        "external_id",
        "created_at",
    )
    list_filter = ("status", "provider")
    search_fields = ("order_id", "external_id", "user__email")
    readonly_fields = ("raw_payload", "created_at", "updated_at", "idempotency_key")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.status == Payment.Status.SUCCESS:
            from src.accounts.models import UserProfile

            UserProfile.for_user(obj.user).mark_paid()
