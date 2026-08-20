from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from src.accounts.models import UserProfile

User = get_user_model()


class PaymentStartPageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="pay@example.com",
            email="pay@example.com",
            password="ComplexPass123!",
        )
        UserProfile.objects.create(
            user=self.user,
            full_name="Pay User",
            phone="+380501112233",
            payment_status=UserProfile.PaymentStatus.UNPAID,
        )

    def test_start_uses_faq_panel(self):
        self.client.force_login(self.user)
        with translation.override("uk"):
            response = self.client.get(reverse("payments:start"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "qm-faq")
        self.assertContains(response, "qm-pay")
        self.assertContains(response, "Не оплачено")
        self.assertContains(response, "До кабінету")

    def test_start_russian_lead(self):
        self.client.force_login(self.user)
        with translation.override("ru"):
            response = self.client.get(reverse("payments:start"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Оплатите участие, чтобы открыть первую комнату.")
        self.assertNotContains(response, "Оплатіть участь, щоб відкрити першу кімнату.")

    @override_settings(PAYMENTS_DEV_BYPASS=True, DEBUG=False)
    def test_dev_bypass_without_debug(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("payments:start"),
            {"action": "dev_bypass"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("quest:room", kwargs={"n": 1}))
        profile = UserProfile.objects.get(user=self.user)
        self.assertTrue(profile.is_paid)
