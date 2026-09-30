"""Unit tests: service layer, no HTTP."""
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from users import services


class RegisterUserTests(TestCase):
    def test_password_is_hashed(self):
        user = services.register_user(username="alice", email="a@example.com", password="S3cure-pass!")
        self.assertNotEqual(user.password, "S3cure-pass!")
        self.assertTrue(user.password.startswith("pbkdf2_sha256$"))
        self.assertTrue(user.check_password("S3cure-pass!"))

    def test_weak_password_rejected_and_not_saved(self):
        with self.assertRaises(ValidationError):
            services.register_user(username="bob", email="b@example.com", password="12345678")
        self.assertFalse(get_user_model().objects.filter(username="bob").exists())


class LoginUserTests(TestCase):
    def setUp(self):
        services.register_user(username="alice", email="a@example.com", password="S3cure-pass!")

    def test_valid_credentials_return_token_pair(self):
        tokens = services.login_user(username="alice", password="S3cure-pass!")
        self.assertEqual(set(tokens), {"access", "refresh"})

    def test_wrong_password_raises(self):
        with self.assertRaises(services.InvalidCredentials):
            services.login_user(username="alice", password="wrong-pass")


class LogoutUserTests(TestCase):
    def setUp(self):
        services.register_user(username="alice", email="a@example.com", password="S3cure-pass!")
        self.refresh = services.login_user(username="alice", password="S3cure-pass!")["refresh"]

    def test_refresh_token_cannot_be_reused_after_logout(self):
        services.logout_user(refresh=self.refresh)
        with self.assertRaises(services.InvalidToken):
            services.logout_user(refresh=self.refresh)

    def test_garbage_token_raises(self):
        with self.assertRaises(services.InvalidToken):
            services.logout_user(refresh="not-a-token")
