from django.contrib.staticfiles.finders import find
from django.core.files import File
from django.core.management.base import BaseCommand

from src.core.models import SiteSettings

STATIC_LOGO = "images/logo-quest-marathon.png"
FILENAME = "logo-km-horizontal.png"


class Command(BaseCommand):
    help = "Copy static logo into SiteSettings.logo (overwrite)."

    def handle(self, *args, **options):
        abs_path = find(STATIC_LOGO)
        if not abs_path:
            self.stderr.write(self.style.ERROR(f"static file not found: {STATIC_LOGO}"))
            return

        settings = SiteSettings.get_solo()
        if settings.logo:
            settings.logo.delete(save=False)
        with open(abs_path, "rb") as fh:
            settings.logo.save(FILENAME, File(fh), save=True)

        self.stdout.write(
            self.style.SUCCESS(f"SiteSettings.logo ← {settings.logo.name}")
        )
