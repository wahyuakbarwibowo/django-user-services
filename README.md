# django-user-services

User auth API (Django + DRF): register, login (token), user detail.

## Endpoints

| Method | Path                   | Auth            | Body                              |
|--------|------------------------|-----------------|-----------------------------------|
| POST   | `/api/auth/register/`  | -               | `username`, `email`, `password`   |
| POST   | `/api/auth/login/`     | -               | `username`, `password` → `token`  |
| GET    | `/api/auth/me/`        | `Token <token>` | -                                 |

Passwords are hashed with PBKDF2-SHA256 (Django default) and checked against Django's password validators.

## Layout

- `users/services.py` — business logic (register, login)
- `users/serializers.py` — input validation / output shape
- `users/views.py` — thin HTTP layer
- `users/tests/test_services.py` — unit tests
- `users/tests/test_api.py` — integration tests (HTTP → DB)

## Dev

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py test
```

## Docker

```bash
cp .env.example .env   # set DJANGO_SECRET_KEY
docker compose up --build
```

SQLite lives in the `sqlite-data` volume. `db.sqlite3` is git-ignored.

## CI

`.github/workflows/ci.yml` is disabled (`if: ${{ false }}`). Remove that line per job to enable.
