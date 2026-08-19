from django.test import TestCase
from django.urls import reverse

from src.pages.faq import parse_faq_items
from src.pages.legal import parse_legal_document
from src.pages.models import InfoPage


class ParseFaqItemsTests(TestCase):
    def test_splits_question_and_answer(self):
        body = (
            "Як почати?\n"
            "Зареєструйтесь.\n\n"
            "Чи зберігається прогрес?\n"
            "Так."
        )
        items = parse_faq_items(body)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["question"], "Як почати?")
        self.assertEqual(items[0]["answer"], "Зареєструйтесь.")


class FaqPageTests(TestCase):
    def setUp(self):
        InfoPage.objects.create(
            slug="faq",
            locale="uk",
            title="FAQ",
            body="Як почати?\nЗареєструйтесь, оплатіть участь.",
            is_published=True,
        )

    def test_faq_renders_accordion(self):
        response = self.client.get(reverse("pages:faq"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "qm-faq__item")
        self.assertContains(response, "Як почати?")
        self.assertContains(response, "Зареєструйтесь, оплатіть участь.")


class AboutContactsTests(TestCase):
    def setUp(self):
        InfoPage.objects.create(
            slug="about",
            locale="uk",
            title="Про нас",
            body=(
                "Що таке квест?\n"
                "Лінійний онлайн-квест.\n\n"
                "Як проходити?\n"
                "По черзі.\n\n"
                "Відповідь?\n"
                "Ключове слово.\n\n"
                "Прогрес?\n"
                "Зберігається."
            ),
            is_published=True,
        )
        InfoPage.objects.create(
            slug="contacts",
            locale="uk",
            title="Контакти",
            body="",
            is_published=True,
        )

    def test_about_has_no_accordion(self):
        response = self.client.get(reverse("pages:about"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<details")
        self.assertContains(response, "qm-about-card")
        self.assertContains(response, "Що таке квест?")
        self.assertContains(response, "Лінійний онлайн-квест.")

    def test_contacts_shows_test_details_and_socials(self):
        response = self.client.get(reverse("pages:contacts"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<details")
        self.assertContains(response, "mailto:info@example.com")
        self.assertContains(response, "tel:+380930001122")
        self.assertContains(response, "t.me/kvestmarafon")
        self.assertContains(response, "instagram.com/kvestmarafon")
        self.assertContains(response, "facebook.com/kvestmarafon")


class ParseLegalDocumentTests(TestCase):
    def test_splits_updated_and_sections(self):
        body = (
            "Останнє оновлення: 19 серпня 2026 р.\n"
            "\n"
            "1. Загальні положення\n"
            "\n"
            "1.1. Перший пункт.\n"
            "\n"
            "1.2. Другий пункт.\n"
            "\n"
            "2. Предмет Угоди\n"
            "\n"
            "2.1. Доступ до квесту."
        )
        parsed = parse_legal_document(body)
        self.assertEqual(parsed["updated"], "Останнє оновлення: 19 серпня 2026 р.")
        self.assertEqual(len(parsed["items"]), 2)
        self.assertEqual(parsed["items"][0]["question"], "1. Загальні положення")
        self.assertIn("1.1. Перший пункт.", parsed["items"][0]["answer"])
        self.assertIn("1.2. Другий пункт.", parsed["items"][0]["answer"])
        self.assertEqual(parsed["items"][1]["question"], "2. Предмет Угоди")


class LegalPageTests(TestCase):
    def setUp(self):
        InfoPage.objects.create(
            slug="terms",
            locale="uk",
            title="Користувацька угода",
            body=(
                "Останнє оновлення: 19 серпня 2026 р.\n"
                "\n"
                "1. Загальні положення\n"
                "\n"
                "1.1. Ця угода регулює доступ."
            ),
            is_published=True,
        )
        InfoPage.objects.create(
            slug="privacy",
            locale="uk",
            title="Політика конфіденційності",
            body=(
                "Останнє оновлення: 19 серпня 2026 р.\n"
                "\n"
                "1. Хто обробляє дані\n"
                "\n"
                "1.1. Володільцем є Організатор."
            ),
            is_published=True,
        )

    def test_terms_renders_accordion(self):
        response = self.client.get(reverse("pages:terms"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "qm-faq--legal")
        self.assertContains(response, "qm-faq__item")
        self.assertContains(response, "1. Загальні положення")
        self.assertContains(response, "Ця угода регулює доступ.")
        self.assertContains(response, "Останнє оновлення: 19 серпня 2026 р.")

    def test_privacy_renders_accordion(self):
        response = self.client.get(reverse("pages:privacy"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "qm-faq--legal")
        self.assertContains(response, "1. Хто обробляє дані")
        self.assertContains(response, "Володільцем є Організатор.")
