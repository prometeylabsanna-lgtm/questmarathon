from django.urls import path

from src.quest import views

app_name = "quest_api"

urlpatterns = [
    path("room/<int:n>/check/", views.check_keyword, name="check"),
]
