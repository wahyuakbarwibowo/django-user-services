"""Business logic for user auth, kept framework-agnostic from the HTTP layer."""
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

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


class InvalidToken(Exception):
    pass


def login_user(*, username: str, password: str) -> dict:
    user = authenticate(username=username, password=password)
    if user is None:
        raise InvalidCredentials
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


def logout_user(*, refresh: str) -> None:
    try:
        RefreshToken(refresh).blacklist()
    except TokenError as exc:
        raise InvalidToken from exc
