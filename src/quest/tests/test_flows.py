from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from src.accounts.models import UserProfile
from src.core.models import SiteStats
from src.payments.models import Payment
from src.payments.services.liqpay import LiqPayService
from src.quest.models import QuestRoom, normalize_keyword

User = get_user_model()


class NormalizeKeywordTests(TestCase):
    def test_strip_and_casefold(self):
        self.assertEqual(normalize_keyword("  Ключ "), "ключ")
        self.assertEqual(normalize_keyword("KEY"), "key")


class QuestGateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="player@example.com",
            email="player@example.com",
            password="Secret123!",
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            full_name="Player",
            phone="+380000000000",
            payment_status=UserProfile.PaymentStatus.PAID,
            current_level=1,
        )
        for n in range(1, 6):
            QuestRoom.objects.create(
                order=n,
                title_uk=f"Room {n}",
                keyword_normalized=f"key{n}",
            )

    def test_skip_room_denied(self):
        self.client.login(username="player@example.com", password="Secret123!")
        response = self.client.get(reverse("quest:room", kwargs={"n": 3}))
        self.assertEqual(response.status_code, 403)

    def test_check_keyword_advances(self):
        self.client.login(username="player@example.com", password="Secret123!")
        response = self.client.post(
            reverse("quest_api:check", kwargs={"n": 2}),
            {"keyword": " KEY2 "},
        )
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.current_level, 2)
        self.assertIn("HX-Redirect", response.headers)


class CounterTests(TestCase):
    def test_paid_only(self):
        paid = User.objects.create_user("a@x.com", "a@x.com", "Secret123!")
        unpaid = User.objects.create_user("b@x.com", "b@x.com", "Secret123!")
        UserProfile.objects.create(
            user=paid,
            full_name="A",
            phone="1",
            payment_status=UserProfile.PaymentStatus.PAID,
        )
        UserProfile.objects.create(
            user=unpaid,
            full_name="B",
            phone="2",
            payment_status=UserProfile.PaymentStatus.UNPAID,
        )
        count = SiteStats.sync_from_profiles()
        self.assertEqual(count, 1)


class LiqPayWebhookTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("pay@x.com", "pay@x.com", "Secret123!")
        self.profile = UserProfile.objects.create(
            user=self.user,
            full_name="Pay",
            phone="1",
        )
        self.payment = Payment.objects.create(
            user=self.user,
            order_id="qm-test-1",
            amount="100.00",
            status=Payment.Status.PENDING,
        )

    @override_settings(LIQPAY_PUBLIC_KEY="pub", LIQPAY_PRIVATE_KEY="priv")
    def test_webhook_marks_paid_idempotent(self):
        service = LiqPayService("pub", "priv")
        payload = {
            "order_id": "qm-test-1",
            "status": "success",
            "payment_id": "999",
        }
        import base64
        import json

        data_b64 = base64.b64encode(
            json.dumps(payload, ensure_ascii=False).encode()
        ).decode()
        signature = service._sign(data_b64)

        url = reverse("payments_api:webhook_liqpay")
        r1 = self.client.post(url, {"data": data_b64, "signature": signature})
        self.assertEqual(r1.status_code, 200)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.is_paid)

        r2 = self.client.post(url, {"data": data_b64, "signature": signature})
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(SiteStats.sync_from_profiles(), 1)
