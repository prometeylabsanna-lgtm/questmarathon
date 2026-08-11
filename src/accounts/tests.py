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
