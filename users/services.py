"""Business logic for user auth, kept framework-agnostic from the HTTP layer."""
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework.authtoken.models import Token

User = get_user_model()


class InvalidCredentials(Exception):
    pass


@transaction.atomic
def register_user(*, username: str, email: str, password: str):
    user = User(username=username, email=email)
    validate_password(password, user)
    user.set_password(password)  # hashed, never stored raw
    user.save()
    return user


def login_user(*, username: str, password: str) -> str:
    user = authenticate(username=username, password=password)
    if user is None:
        raise InvalidCredentials
    token, _ = Token.objects.get_or_create(user=user)
    return token.key
