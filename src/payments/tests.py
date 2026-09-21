import base64
import json

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from src.accounts.models import UserProfile
from src.payments.models import Payment
from src.payments.services.liqpay import LiqPayService

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
        self.assertContains(response, "Симулювати оплату")

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

    @override_settings(
        LIQPAY_PUBLIC_KEY="pub",
        LIQPAY_PRIVATE_KEY="priv",
        LIQPAY_SANDBOX=False,
        PAYMENTS_DEV_BYPASS=True,
    )
    def test_live_keys_ignore_bypass_and_send_sandbox_zero(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("payments:start"),
            {"action": "dev_bypass"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "liqpay-checkout")
        self.assertNotContains(response, "Симулювати оплату")
        profile = UserProfile.objects.get(user=self.user)
        self.assertFalse(profile.is_paid)
        payload = json.loads(base64.b64decode(response.context["liqpay_data"]))
        self.assertEqual(payload["sandbox"], 0)
        self.assertEqual(payload["action"], "pay")
        self.assertEqual(payload["public_key"], "pub")
        payment = Payment.objects.get(user=self.user)
        self.assertEqual(payment.status, Payment.Status.PENDING)

    @override_settings(
        LIQPAY_PUBLIC_KEY="pub",
        LIQPAY_PRIVATE_KEY="priv",
        LIQPAY_SANDBOX=True,
    )
    def test_configured_checkout_sandbox_one(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("payments:start"))
        self.assertEqual(response.status_code, 200)
        payload = json.loads(base64.b64decode(response.context["liqpay_data"]))
        self.assertEqual(payload["sandbox"], 1)
        self.assertNotContains(response, "Симулювати оплату")


class LiqPayCheckoutPayloadTests(TestCase):
    def test_sandbox_flag_follows_setting(self):
        service = LiqPayService("pub", "priv")
        with override_settings(LIQPAY_SANDBOX=False):
            live = service.create_checkout_data(
                order_id="qm-1",
                amount="100.00",
                description="test",
                result_url="https://example.com/return/",
                server_url="https://example.com/hook/",
            )
        with override_settings(LIQPAY_SANDBOX=True):
            test = service.create_checkout_data(
                order_id="qm-1",
                amount="100.00",
                description="test",
                result_url="https://example.com/return/",
                server_url="https://example.com/hook/",
            )
        live_payload = json.loads(base64.b64decode(live["data"]))
        test_payload = json.loads(base64.b64decode(test["data"]))
        self.assertEqual(live_payload["sandbox"], 0)
        self.assertEqual(test_payload["sandbox"], 1)
        self.assertEqual(live["checkout_url"], "https://www.liqpay.ua/api/3/checkout")
