from django.urls import path

from src.pages import views

app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about_page, name="about"),
    path("faq/", views.faq_page, name="faq"),
    path("contacts/", views.contacts_page, name="contacts"),
    path("rating/", views.rating, name="rating"),
    path("terms/", views.legal_page, {"slug": "terms"}, name="terms"),
    path("privacy/", views.legal_page, {"slug": "privacy"}, name="privacy"),
]
