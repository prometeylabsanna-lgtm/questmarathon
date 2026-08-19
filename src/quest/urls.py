from django.urls import path

from src.quest import views

app_name = "quest"

urlpatterns = [
    path("room/<int:n>/", views.room, name="room"),
    path("room/<int:n>/check/", views.check_keyword, name="check"),
]
