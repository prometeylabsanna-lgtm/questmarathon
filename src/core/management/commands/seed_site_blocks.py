from django.core.management.base import BaseCommand

from src.core.management.commands.seed_demo import seed_site_blocks
from src.core.site_content_registry import validate_registry


class Command(BaseCommand):
    help = "Idempotent seed of SiteBlock rows from registry defaults"

    def handle(self, *args, **options):
        validate_registry()
        created = seed_site_blocks()
        self.stdout.write(self.style.SUCCESS(f"Created {created} SiteBlock rows"))
