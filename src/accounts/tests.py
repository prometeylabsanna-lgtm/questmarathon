from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class RegisterTests(TestCase):
    def test_register_redirects_to_payment(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "email": "reg@example.com",
                "full_name": "Reg User",
                "phone": "+380501112233",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
                "consent_terms": True,
                "consent_age18": True,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("payments:start"))
        user = User.objects.get(email="reg@example.com")
        self.assertTrue(hasattr(user, "profile"))
        self.assertEqual(user.username, "reg@example.com")


class CabinetTests(TestCase):
    def test_cabinet_renders_for_logged_in_user(self):
        user = User.objects.create_user(
            username="cab@example.com",
            email="cab@example.com",
            password="ComplexPass123!",
        )
        self.client.force_login(user)
        response = self.client.get(reverse("accounts:cabinet"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Кабінет")
