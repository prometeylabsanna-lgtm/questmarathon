from django.urls import path

from src.payments import views

app_name = "payments"

urlpatterns = [
    path("start/", views.payment_start, name="start"),
    path("return/", views.payment_return, name="return"),
]
