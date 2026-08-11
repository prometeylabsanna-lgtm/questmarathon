from django.urls import path

from src.payments import views

app_name = "payments_api"

urlpatterns = [
    path("webhook/liqpay/", views.payment_webhook_liqpay, name="webhook_liqpay"),
]
