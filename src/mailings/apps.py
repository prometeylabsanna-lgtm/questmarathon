from django.apps import AppConfig


class MailingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "src.mailings"
    label = "mailings"
    verbose_name = "Mailings"
