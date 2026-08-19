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

    def test_room_required_hint_follows_ui_locale(self):
        self.client.login(username="player@example.com", password="Secret123!")
        uk = self.client.get(reverse("quest:room", kwargs={"n": 1}))
        self.assertContains(uk, 'data-required-msg="Заповніть це поле."')
        ru = self.client.get("/ru/quest/room/1/")
        self.assertContains(ru, 'data-required-msg="Заполните это поле."')
        self.assertNotContains(ru, 'data-required-msg="Заповніть це поле."')

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

    def test_last_room_sets_hx_redirect_to_cabinet(self):
        self.profile.current_level = 4
        self.profile.save(update_fields=["current_level", "updated_at"])
        self.client.login(username="player@example.com", password="Secret123!")
        response = self.client.post(
            reverse("quest:check", kwargs={"n": 5}),
            {"keyword": "key5"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["HX-Redirect"], reverse("accounts:cabinet"))

    def test_wrong_keyword_uses_russian_when_prefixed(self):
        self.client.login(username="player@example.com", password="Secret123!")
        response = self.client.post(
            "/ru/quest/room/2/check/",
            {"keyword": "wrong"},
        )
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn("Неверное ключевое слово", body)
        self.assertNotIn("Невірне ключове слово", body)

    def test_wrong_keyword_uses_russian_from_htmx_current_url(self):
        self.client.login(username="player@example.com", password="Secret123!")
        response = self.client.post(
            reverse("quest_api:check", kwargs={"n": 2}),
            {"keyword": "wrong"},
            headers={"HX-Current-URL": "http://testserver/ru/quest/room/2/"},
        )
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn("Неверное ключевое слово", body)
        self.assertNotIn("Невірне ключове слово", body)


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
            currency="UAH",
            status=Payment.Status.PENDING,
        )

    def _post_webhook(self, payload, signature=None):
        import base64
        import json

        service = LiqPayService("pub", "priv")
        data_b64 = base64.b64encode(
            json.dumps(payload, ensure_ascii=False).encode()
        ).decode()
        if signature is None:
            signature = service._sign(data_b64)
        url = reverse("payments_api:webhook_liqpay")
        return self.client.post(url, {"data": data_b64, "signature": signature})

    @override_settings(LIQPAY_PUBLIC_KEY="pub", LIQPAY_PRIVATE_KEY="priv")
    def test_webhook_marks_paid_idempotent(self):
        payload = {
            "order_id": "qm-test-1",
            "status": "success",
            "payment_id": "999",
            "amount": "100.00",
            "currency": "UAH",
        }
        r1 = self._post_webhook(payload)
        self.assertEqual(r1.status_code, 200)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.is_paid)
        self.assertEqual(self.profile.current_level, 0)

        r2 = self._post_webhook(payload)
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(SiteStats.sync_from_profiles(), 1)

    @override_settings(LIQPAY_PUBLIC_KEY="pub", LIQPAY_PRIVATE_KEY="priv")
    def test_wait_accept_does_not_mark_paid(self):
        payload = {
            "order_id": "qm-test-1",
            "status": "wait_accept",
            "payment_id": "999",
            "amount": "100.00",
            "currency": "UAH",
        }
        response = self._post_webhook(payload)
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.payment.refresh_from_db()
        self.assertFalse(self.profile.is_paid)
        self.assertEqual(self.payment.status, Payment.Status.PENDING)

    @override_settings(LIQPAY_PUBLIC_KEY="pub", LIQPAY_PRIVATE_KEY="priv")
    def test_amount_mismatch_rejected(self):
        payload = {
            "order_id": "qm-test-1",
            "status": "success",
            "payment_id": "999",
            "amount": "1.00",
            "currency": "UAH",
        }
        response = self._post_webhook(payload)
        self.assertEqual(response.status_code, 400)
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.is_paid)

    @override_settings(LIQPAY_PUBLIC_KEY="pub", LIQPAY_PRIVATE_KEY="priv")
    def test_invalid_signature_rejected(self):
        payload = {
            "order_id": "qm-test-1",
            "status": "success",
            "payment_id": "999",
            "amount": "100.00",
            "currency": "UAH",
        }
        response = self._post_webhook(payload, signature="not-a-valid-signature")
        self.assertEqual(response.status_code, 403)

    @override_settings(LIQPAY_PUBLIC_KEY="pub", LIQPAY_PRIVATE_KEY="priv")
    def test_start_reuses_pending_payment(self):
        self.client.login(username="pay@x.com", password="Secret123!")
        url = reverse("payments:start")
        self.client.get(url)
        self.client.get(url)
        self.assertEqual(Payment.objects.filter(user=self.user).count(), 1)
