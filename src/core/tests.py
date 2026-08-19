from django.test import RequestFactory, TestCase
from django.utils import translation

from src.core.i18n import activate_ui_language


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
