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


class AboutContactsAccordionTests(TestCase):
    def setUp(self):
        InfoPage.objects.create(
            slug="about",
            locale="uk",
            title="Про нас",
            body="Що таке квест?\nЛінійний онлайн-квест.",
            is_published=True,
        )
        InfoPage.objects.create(
            slug="contacts",
            locale="uk",
            title="Контакти",
            body="Як зв’язатися?\nНапишіть нам.\n\nEmail\ninfo@example.com",
            is_published=True,
        )

    def test_about_renders_accordion(self):
        response = self.client.get(reverse("pages:about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "qm-faq__item")
        self.assertContains(response, "Що таке квест?")

    def test_contacts_email_is_mailto(self):
        response = self.client.get(reverse("pages:contacts"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "mailto:info@example.com")
        self.assertContains(response, "Як зв’язатися?")
