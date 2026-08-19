from django.contrib.auth import get_user_model
from django.test import TestCase
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
