from django.urls import path

from src.accounts import views

app_name = "accounts"

urlpatterns = [
    path("cabinet/", views.cabinet, name="cabinet"),
    path("auth/login/", views.QuestLoginView.as_view(), name="login"),
    path("auth/register/", views.register, name="register"),
    path("auth/logout/", views.QuestLogoutView.as_view(), name="logout"),
    path(
        "auth/password-reset/",
        views.QuestPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "auth/password-reset/done/",
        views.QuestPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "auth/password-reset/<uidb64>/<token>/",
        views.QuestPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "auth/password-reset/complete/",
        views.QuestPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
