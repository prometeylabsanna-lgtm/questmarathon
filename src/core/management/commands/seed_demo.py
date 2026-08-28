from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from decouple import config

from src.core.block_defaults import (
    BLOCK_CONTENT_TYPES,
    BLOCK_DEFAULTS,
    BLOCK_LABELS,
    is_visibility_key,
)
from src.core.models import SiteBlock, SiteSettings, SiteStats
from src.core.site_content_registry import all_registry_block_keys, validate_registry
from src.pages.faq import parse_faq_items
from src.pages.legal_html import plain_legal_to_html
from src.pages.legal_texts import PRIVACY_RU, PRIVACY_UK, TERMS_RU, TERMS_UK
from src.pages.models import AboutCard, FAQItem, InfoPage, LegalPage
from src.quest.models import QuestRoom

ABOUT_UK = (
    "Що таке «Квест-марафон»?\n"
    "«Квест-марафон» — лінійний онлайн-квест із п’яти кімнат. Це не гілка з розвилками і не вікторина з підказок: один маршрут, одна загадка за раз.\n"
    "Гра розрахована на самостійне проходження — у зручному темпі, без сторонніх підказок.\n\n"
    "Як проходити кімнати?\n"
    "Після реєстрації й оплати відкривається перша кімната. Далі кімнати йдуть строго по черзі до п’ятої: пропустити етап не можна — наступна відкриється лише після правильного ключового слова.\n\n"
    "Що є відповіддю?\n"
    "У кожній кімнаті — своє завдання: текст, зображення, PDF, аудіо чи відео. Розгадайте загадку й введіть одне ключове слово.\n"
    "Регістр літер і зайві пробіли не мають значення. Слово одне для української та російської версій інтерфейсу.\n\n"
    "Чи зберігається прогрес?\n"
    "Так. Обліковий запис пам’ятає, до якої кімнати ви дійшли. Можна вийти, закрити браузер і пізніше продовжити з того самого місця.\n"
    "Прогрес не обнуляється: повертаєтесь — і гра чекає на наступній відкритій кімнаті."
)

ABOUT_RU = (
    "Что такое «Квест-марафон»?\n"
    "«Квест-марафон» — линейный онлайн-квест из пяти комнат. Это не ветка с развилками и не викторина с подсказками: один маршрут, одна загадка за раз.\n"
    "Игра рассчитана на самостоятельное прохождение — в удобном темпе, без подсказок со стороны.\n\n"
    "Как проходить комнаты?\n"
    "После регистрации и оплаты открывается первая комната. Дальше комнаты идут строго по порядку до пятой: пропустить этап нельзя — следующая откроется только после верного ключевого слова.\n\n"
    "Что является ответом?\n"
    "В каждой комнате — своё задание: текст, изображение, PDF, аудио или видео. Разгадайте загадку и введите одно ключевое слово.\n"
    "Регистр букв и лишние пробелы не имеют значения. Слово одно для украинской и русской версий интерфейса.\n\n"
    "Сохраняется ли прогресс?\n"
    "Да. Аккаунт помнит, до какой комнаты вы дошли. Можно выйти, закрыть браузер и позже продолжить с того же места.\n"
    "Прогресс не обнуляется: возвращаетесь — и игра ждёт на следующей открытой комнате."
)

FAQ_UK = (
    "Як почати?\nЗареєструйтесь, оплатіть участь — і відкриється перша кімната.\n\n"
    "Чи можна пропускати кімнати?\nНі. Наступна кімната відкривається лише після правильного ключового слова.\n\n"
    "Ключове слово різне для української та російської?\nНі, слово одне для обох мов. Регістр літер і зайві пробіли не мають значення.\n\n"
    "Що буде після п’ятої кімнати?\nОкремого фінішного екрана немає. Квест пройдено, усі п’ять кімнат залишаються доступними.\n\n"
    "Чи зберігається прогрес?\nТак. Можна вийти з акаунта і продовжити пізніше."
)

FAQ_RU = (
    "Как начать?\nЗарегистрируйтесь, оплатите участие — и откроется первая комната.\n\n"
    "Можно ли пропускать комнаты?\nНет. Следующая комната открывается только после верного ключевого слова.\n\n"
    "Ключевое слово разное для украинского и русского?\nНет, слово одно для обоих языков. Регистр букв и лишние пробелы не имеют значения.\n\n"
    "Что будет после пятой комнаты?\nОтдельного финального экрана нет. Квест пройден, все пять комнат остаются доступными.\n\n"
    "Сохраняется ли прогресс?\nДа. Можно выйти из аккаунта и продолжить позже."
)

ROOMS = [
    (1, "Кімната 1", "Комната 1", "ключ1"),
    (2, "Кімната 2", "Комната 2", "ключ2"),
    (3, "Кімната 3", "Комната 3", "ключ3"),
    (4, "Кімната 4", "Комната 4", "ключ4"),
    (5, "Кімната 5", "Комната 5", "ключ5"),
]


def seed_site_blocks() -> int:
    created = 0
    for page, key in all_registry_block_keys():
        defaults = BLOCK_DEFAULTS.get((page, key), {})
        ctype = BLOCK_CONTENT_TYPES.get((page, key), SiteBlock.ContentType.TEXT)
        label = BLOCK_LABELS.get((page, key), key)
        _, was_created = SiteBlock.objects.get_or_create(
            page=page,
            key=key,
            defaults={
                "label": label,
                "content_type": ctype,
                "text_uk": defaults.get(
                    "text_uk", "1" if is_visibility_key(key) else ""
                ),
                "text_ru": defaults.get(
                    "text_ru", "1" if is_visibility_key(key) else ""
                ),
            },
        )
        if was_created:
            created += 1
    return created


def seed_legal_from_texts() -> None:
    for slug, title_uk, title_ru, body_uk, body_ru in (
        ("terms", "Користувацька угода", "Пользовательское соглашение", TERMS_UK, TERMS_RU),
        (
            "privacy",
            "Політика конфіденційності",
            "Политика конфиденциальности",
            PRIVACY_UK,
            PRIVACY_RU,
        ),
    ):
        updated_uk, html_uk = plain_legal_to_html(body_uk)
        updated_ru, html_ru = plain_legal_to_html(body_ru)
        LegalPage.objects.get_or_create(
            slug=slug,
            defaults={
                "title_uk": title_uk,
                "title_ru": title_ru,
                "body_uk": html_uk,
                "body_ru": html_ru,
                "updated_label_uk": updated_uk,
                "updated_label_ru": updated_ru,
                "is_published": True,
            },
        )


def seed_faq() -> None:
    if FAQItem.objects.exists():
        return
    uk_items = parse_faq_items(FAQ_UK)
    ru_items = parse_faq_items(FAQ_RU)
    for idx, uk in enumerate(uk_items):
        ru = ru_items[idx] if idx < len(ru_items) else {"question": "", "answer": ""}
        FAQItem.objects.create(
            question_uk=uk["question"],
            answer_uk=uk["answer"],
            question_ru=ru["question"],
            answer_ru=ru["answer"],
            sort_order=idx,
            is_active=True,
        )


def seed_about_cards() -> None:
    if AboutCard.objects.exists():
        return
    uk_items = parse_faq_items(ABOUT_UK)
    ru_items = parse_faq_items(ABOUT_RU)
    for idx, uk in enumerate(uk_items):
        ru = ru_items[idx] if idx < len(ru_items) else {"question": "", "answer": ""}
        AboutCard.objects.create(
            title_uk=uk["question"],
            text_uk=uk["answer"],
            title_ru=ru["question"],
            text_ru=ru["answer"],
            sort_order=idx,
            is_active=True,
        )


def migrate_infopage_if_needed() -> None:
    """One-shot: fill CMS from legacy InfoPage when CMS tables empty."""
    if not LegalPage.objects.exists() and InfoPage.objects.filter(slug="terms").exists():
        for slug in ("terms", "privacy"):
            uk = InfoPage.objects.filter(slug=slug, locale="uk").first()
            ru = InfoPage.objects.filter(slug=slug, locale="ru").first()
            if not uk:
                continue
            updated_uk, html_uk = plain_legal_to_html(uk.body)
            updated_ru, html_ru = ("", "")
            if ru:
                updated_ru, html_ru = plain_legal_to_html(ru.body)
            LegalPage.objects.get_or_create(
                slug=slug,
                defaults={
                    "title_uk": uk.title,
                    "title_ru": ru.title if ru else "",
                    "body_uk": html_uk,
                    "body_ru": html_ru,
                    "updated_label_uk": updated_uk,
                    "updated_label_ru": updated_ru,
                    "is_published": uk.is_published,
                },
            )

    if not FAQItem.objects.exists():
        uk = InfoPage.objects.filter(slug="faq", locale="uk").first()
        ru = InfoPage.objects.filter(slug="faq", locale="ru").first()
        if uk:
            uk_items = parse_faq_items(uk.body)
            ru_items = parse_faq_items(ru.body) if ru else []
            for idx, item in enumerate(uk_items):
                r = ru_items[idx] if idx < len(ru_items) else {"question": "", "answer": ""}
                FAQItem.objects.create(
                    question_uk=item["question"],
                    answer_uk=item["answer"],
                    question_ru=r["question"],
                    answer_ru=r["answer"],
                    sort_order=idx,
                )

    if not AboutCard.objects.exists():
        uk = InfoPage.objects.filter(slug="about", locale="uk").first()
        ru = InfoPage.objects.filter(slug="about", locale="ru").first()
        if uk:
            uk_items = parse_faq_items(uk.body)
            ru_items = parse_faq_items(ru.body) if ru else []
            for idx, item in enumerate(uk_items):
                r = ru_items[idx] if idx < len(ru_items) else {"question": "", "answer": ""}
                AboutCard.objects.create(
                    title_uk=item["question"],
                    text_uk=item["answer"],
                    title_ru=r["question"],
                    text_ru=r["answer"],
                    sort_order=idx,
                )


def seed_staff_user(stdout=None) -> str:
    """
    Create staff superuser from env if missing.
    Requires ADMIN_PASSWORD. Does not overwrite an existing user's password
    unless ADMIN_PASSWORD_FORCE=True.
    """
    password = config("ADMIN_PASSWORD", default="")
    if not password:
        return "skipped (set ADMIN_PASSWORD to bootstrap)"
    username = config("ADMIN_USERNAME", default="admin")
    email = config("ADMIN_EMAIL", default="admin@example.com")
    force = config("ADMIN_PASSWORD_FORCE", default=False, cast=bool)
    User = get_user_model()
    user = User.objects.filter(username=username).first()
    if user is None:
        User.objects.create_superuser(username=username, email=email, password=password)
        return f"created {username}"
    changed = False
    if not user.is_staff or not user.is_superuser or not user.is_active:
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        changed = True
    if force:
        user.set_password(password)
        changed = True
    if changed:
        user.save()
        return f"updated {username}"
    return f"exists {username}"


class Command(BaseCommand):
    help = "Idempotent seed: rooms, SiteSettings, SiteBlocks, Legal/FAQ/About CMS"

    @transaction.atomic
    def handle(self, *args, **options):
        validate_registry()
        SiteStats.get_solo()
        SiteSettings.get_solo()

        self.stdout.write(f"staff user: {seed_staff_user()}")

        for order, title_uk, title_ru, keyword in ROOMS:
            obj, created = QuestRoom.objects.get_or_create(
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
            self.stdout.write(f"{'created' if created else 'exists'} room {obj.order}")

        n = seed_site_blocks()
        self.stdout.write(f"site blocks created: {n}")

        migrate_infopage_if_needed()
        seed_legal_from_texts()
        seed_faq()
        seed_about_cards()

        SiteStats.sync_from_profiles()
        self.stdout.write(self.style.SUCCESS("seed_demo done"))
