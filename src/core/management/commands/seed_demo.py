from django.core.management.base import BaseCommand
from django.db import transaction

from src.core.models import SiteStats
from src.pages.models import InfoPage
from src.quest.models import QuestRoom

INFO_PAGES = [
    ("about", "Про нас", "О нас", "Текст про проєкт «Квест-марафон».", "Текст о проекте «Квест-марафон»."),
    ("faq", "FAQ", "FAQ", "Часті питання зʼявляться тут.", "Частые вопросы появятся здесь."),
    ("contacts", "Контакти", "Контакты", "Email: info@example.com", "Email: info@example.com"),
    ("terms", "Користувацька угода", "Пользовательское соглашение", "Текст угоди.", "Текст соглашения."),
    ("privacy", "Політика конфіденційності", "Политика конфиденциальности", "Текст політики.", "Текст политики."),
]

ROOMS = [
    (1, "Кімната 1", "Комната 1", "ключ1"),
    (2, "Кімната 2", "Комната 2", "ключ2"),
    (3, "Кімната 3", "Комната 3", "ключ3"),
    (4, "Кімната 4", "Комната 4", "ключ4"),
    (5, "Кімната 5", "Комната 5", "ключ5"),
]


class Command(BaseCommand):
    help = "Idempotent seed: 5 quest rooms + info pages uk/ru + SiteStats"

    @transaction.atomic
    def handle(self, *args, **options):
        SiteStats.get_solo()

        for order, title_uk, title_ru, keyword in ROOMS:
            obj, created = QuestRoom.objects.update_or_create(
                order=order,
                defaults={
                    "title_uk": title_uk,
                    "title_ru": title_ru,
                    "body_uk": f"Завдання кімнати {order}.",
                    "body_ru": f"Задание комнаты {order}.",
                    "keyword_normalized": keyword,
                    "is_active": True,
                },
            )
            self.stdout.write(f"{'created' if created else 'updated'} room {obj.order}")

        for slug, title_uk, title_ru, body_uk, body_ru in INFO_PAGES:
            for locale, title, body in (
                ("uk", title_uk, body_uk),
                ("ru", title_ru, body_ru),
            ):
                obj, created = InfoPage.objects.update_or_create(
                    slug=slug,
                    locale=locale,
                    defaults={
                        "title": title,
                        "body": body,
                        "is_published": True,
                    },
                )
                self.stdout.write(
                    f"{'created' if created else 'updated'} page {obj.slug}/{obj.locale}"
                )

        SiteStats.sync_from_profiles()
        self.stdout.write(self.style.SUCCESS("seed_demo done"))
