from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from src.core.models import SiteBlock, SiteSettings


class SiteContentAdminTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser(
            username="cmsadmin", email="a@b.c", password="pass"
        )
        self.client.force_login(user)
        SiteSettings.get_solo()

    def test_home_intro_get_shows_dark_inputs(self):
        url = reverse("admin:core_homeintrosettings_change", args=[1])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("bg-base-900", content)
        self.assertIn("text-base-100", content)
        self.assertIn("block__home__intro_tagline__text_uk", content)
        start = content.find("block__home__intro_tagline__text_uk")
        snippet = content[start : start + 800]
        self.assertIn("bg-base-900", snippet)
        self.assertIn("text-base-100", snippet)

    def test_home_intro_post_updates_block(self):
        SiteBlock.objects.get_or_create(
            page="home",
            key="intro_tagline",
            defaults={"label": "Tagline", "text_uk": "old", "text_ru": "old"},
        )
        url = reverse("admin:core_homeintrosettings_change", args=[1])
        response = self.client.post(
            url,
            {
                "section_visible": "on",
                "block__home__intro_tagline__text_uk": "Новий tagline",
                "block__home__intro_tagline__text_ru": "Новый tagline",
                "block__home__rules_heading__text_uk": "Правила",
                "block__home__rules_heading__text_ru": "Правила",
                "block__home__rule_1__text_uk": "1",
                "block__home__rule_1__text_ru": "1",
                "block__home__rule_2__text_uk": "2",
                "block__home__rule_2__text_ru": "2",
                "block__home__rule_3__text_uk": "3",
                "block__home__rule_3__text_ru": "3",
                "block__home__rule_4__text_uk": "4",
                "block__home__rule_4__text_ru": "4",
                "block__home__cta_register__text_uk": "Реєстрація",
                "block__home__cta_register__text_ru": "Регистрация",
                "block__home__cta_login__text_uk": "Увійти",
                "block__home__cta_login__text_ru": "Войти",
                "block__home__cta_cabinet__text_uk": "Кабінет",
                "block__home__cta_cabinet__text_ru": "Кабинет",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        block = SiteBlock.objects.get(page="home", key="intro_tagline")
        self.assertEqual(block.text_uk, "Новий tagline")
        self.assertEqual(block.text_ru, "Новый tagline")
