from django.core.management.base import BaseCommand
from django.db import transaction

from src.core.models import SiteStats
from src.pages.legal_texts import PRIVACY_RU, PRIVACY_UK, TERMS_RU, TERMS_UK
from src.pages.models import InfoPage
from src.quest.models import QuestRoom

INFO_PAGES = [
    (
        "about",
        "Про нас",
        "О нас",
        "Що таке «Квест-марафон»?\nЛінійний онлайн-квест із п’яти кімнат.\n\nЯк проходити кімнати?\nПісля реєстрації та оплати ви проходите завдання строго по черзі: від першої кімнати до п’ятої.\n\nЩо є відповіддю?\nУ кожній кімнаті — своя загадка; відповідь — одне ключове слово.\n\nЧи зберігається прогрес?\nТак. Можна вийти і повернутись у будь-який момент.",
        "Что такое «Квест-марафон»?\nЛинейный онлайн-квест из пяти комнат.\n\nКак проходить комнаты?\nПосле регистрации и оплаты вы проходите задания строго по порядку: от первой комнаты к пятой.\n\nЧто является ответом?\nВ каждой комнате — своя загадка; ответ — одно ключевое слово.\n\nСохраняется ли прогресс?\nДа. Можно выйти и вернуться в любой момент.",
    ),
    (
        "faq",
        "FAQ",
        "FAQ",
        "Як почати?\nЗареєструйтесь, оплатіть участь — і відкриється перша кімната.\n\nЧи можна пропускати кімнати?\nНі. Наступна кімната відкривається лише після правильного ключового слова.\n\nКлючове слово різне для української та російської?\nНі, слово одне для обох мов. Регістр літер і зайві пробіли не мають значення.\n\nЩо буде після п’ятої кімнати?\nОкремого фінішного екрана немає. Квест пройдено, усі п’ять кімнат залишаються доступними.\n\nЧи зберігається прогрес?\nТак. Можна вийти з акаунта і продовжити пізніше.",
        "Как начать?\nЗарегистрируйтесь, оплатите участие — и откроется первая комната.\n\nМожно ли пропускать комнаты?\nНет. Следующая комната открывается только после верного ключевого слова.\n\nКлючевое слово разное для украинского и русского?\nНет, слово одно для обоих языков. Регистр букв и лишние пробелы не имеют значения.\n\nЧто будет после пятой комнаты?\nОтдельного финального экрана нет. Квест пройден, все пять комнат остаются доступными.\n\nСохраняется ли прогресс?\nДа. Можно выйти из аккаунта и продолжить позже.",
    ),
    (
        "contacts",
        "Контакти",
        "Контакты",
        "Як зв’язатися?\nЗ питаннями щодо участі, оплати або доступу до квесту напишіть нам.\n\nEmail\ninfo@example.com",
        "Как связаться?\nПо вопросам участия, оплаты или доступа к квесту напишите нам.\n\nEmail\ninfo@example.com",
    ),
    (
        "terms",
        "Користувацька угода",
        "Пользовательское соглашение",
        TERMS_UK,
        TERMS_RU,
    ),
    (
        "privacy",
        "Політика конфіденційності",
        "Политика конфиденциальности",
        PRIVACY_UK,
        PRIVACY_RU,
    ),
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
                    "body_uk": f"Розгадайте загадку кімнати {order} і введіть ключове слово.",
                    "body_ru": f"Разгадайте загадку комнаты {order} и введите ключевое слово.",
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
