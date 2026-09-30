"""Integration tests: full HTTP flow through URLs, views, services and DB."""
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase

PASSWORD = "S3cure-pass!"


class AuthFlowTests(APITestCase):
    def setUp(self):
        cache.clear()  # reset throttle counters between tests

    def login(self, password=PASSWORD):
        return self.client.post(reverse("login"), {"username": "alice", "password": password}, format="json")

    def register(self, **overrides):
        data = {"username": "alice", "email": "a@example.com", "password": PASSWORD, **overrides}
        return self.client.post(reverse("register"), data, format="json")

    def test_register_login_me_flow(self):
        res = self.register()
        self.assertEqual(res.status_code, 201)
        self.assertNotIn("password", res.data)

        res = self.login()
        self.assertEqual(res.status_code, 200)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        res = self.client.get(reverse("me"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["username"], "alice")

    def test_refresh_then_logout_revokes_refresh_token(self):
        self.register()
        tokens = self.login().data

        res = self.client.post(reverse("token-refresh"), {"refresh": tokens["refresh"]}, format="json")
        self.assertEqual(res.status_code, 200)
        new_refresh = res.data["refresh"]  # rotated

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
        res = self.client.post(reverse("logout"), {"refresh": new_refresh}, format="json")
        self.assertEqual(res.status_code, 205)

        res = self.client.post(reverse("token-refresh"), {"refresh": new_refresh}, format="json")
        self.assertEqual(res.status_code, 401)

    def test_logout_requires_auth(self):
        res = self.client.post(reverse("logout"), {"refresh": "x"}, format="json")
        self.assertEqual(res.status_code, 401)

    def test_login_is_rate_limited(self):
        self.register()
        codes = [self.login(password="wrong-pass").status_code for _ in range(6)]
        self.assertEqual(codes[:5], [401] * 5)
        self.assertEqual(codes[5], 429)

    def test_duplicate_username_rejected(self):
        self.register()
        res = self.register(email="other@example.com")
        self.assertEqual(res.status_code, 400)
        self.assertIn("username", res.data)

    def test_duplicate_email_case_insensitive(self):
        self.register()
        res = self.register(username="bob", email="A@EXAMPLE.com")
        self.assertEqual(res.status_code, 400)
        self.assertIn("email", res.data)

    def test_weak_password_rejected(self):
        res = self.register(password="password")
        self.assertEqual(res.status_code, 400)
        self.assertIn("password", res.data)

    def test_login_wrong_password(self):
        self.register()
        self.assertEqual(self.login(password="nope-nope").status_code, 401)

    def test_me_requires_auth(self):
        self.assertEqual(self.client.get(reverse("me")).status_code, 401)
