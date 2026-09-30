FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SQLITE_PATH=/app/data/db.sqlite3

WORKDIR /app
RUN useradd --create-home app && mkdir -p /app/data && chown app /app/data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=app . .
USER app

EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2"]
