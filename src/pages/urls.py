from django.urls import path

from src.pages import views

app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.info_page, {"slug": "about"}, name="about"),
    path("faq/", views.info_page, {"slug": "faq"}, name="faq"),
    path("contacts/", views.info_page, {"slug": "contacts"}, name="contacts"),
    path("terms/", views.info_page, {"slug": "terms"}, name="terms"),
    path("privacy/", views.info_page, {"slug": "privacy"}, name="privacy"),
]
