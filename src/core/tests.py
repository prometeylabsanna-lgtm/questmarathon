from django.test import RequestFactory, TestCase
from django.utils import translation

from src.core.i18n import activate_ui_language, path_for_language


class ActivateUiLanguageTests(TestCase):
    def test_hx_current_url_russian_prefix(self):
        self.addCleanup(translation.deactivate)
        factory = RequestFactory()
        request = factory.post(
            "/api/v1/quest/room/1/check/",
            HTTP_HX_CURRENT_URL="http://testserver/ru/quest/room/1/",
        )
        lang = activate_ui_language(request)
        self.assertEqual(lang, "ru")
        self.assertEqual(translation.get_language(), "ru")


class LanguageUrlsTests(TestCase):
    def test_russian_path_has_ukrainian_counterpart(self):
        self.assertEqual(path_for_language("/ru/about/", "uk"), "/about/")
        self.assertEqual(path_for_language("/ru/about/", "ru"), "/ru/about/")
        self.assertEqual(path_for_language("/about/?v=1", "ru"), "/ru/about/?v=1")
        self.assertEqual(path_for_language("/ru/about/?v=1", "uk"), "/about/?v=1")
