"""Integration tests: full HTTP flow through URLs, views, services and DB."""
from django.urls import reverse
from rest_framework.test import APITestCase

PASSWORD = "S3cure-pass!"


class AuthFlowTests(APITestCase):
    def register(self, **overrides):
        data = {"username": "alice", "email": "a@example.com", "password": PASSWORD, **overrides}
        return self.client.post(reverse("register"), data, format="json")

    def test_register_login_me_flow(self):
        res = self.register()
        self.assertEqual(res.status_code, 201)
        self.assertNotIn("password", res.data)

        res = self.client.post(reverse("login"), {"username": "alice", "password": PASSWORD}, format="json")
        self.assertEqual(res.status_code, 200)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {res.data['token']}")
        res = self.client.get(reverse("me"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["username"], "alice")

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
        res = self.client.post(reverse("login"), {"username": "alice", "password": "nope-nope"}, format="json")
        self.assertEqual(res.status_code, 401)

    def test_me_requires_auth(self):
        self.assertEqual(self.client.get(reverse("me")).status_code, 401)
