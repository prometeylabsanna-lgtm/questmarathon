from django.test import TestCase
from django.urls import reverse

from src.pages.faq import parse_faq_items
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
