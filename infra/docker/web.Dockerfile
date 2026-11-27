FROM python:3.12.16-slim-bookworm@sha256:44cf1793efa7c7a476bb0f2cff81443f4a072c90c1cb127e2924933daa3e8c64

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    DJANGO_SETTINGS_MODULE=allelefounder.config.settings.production

WORKDIR /app

RUN groupadd --gid 10001 allelefounder \
    && useradd --uid 10001 --gid allelefounder --create-home allelefounder

COPY requirements/production.txt requirements/production.txt
RUN pip install --no-cache-dir --require-hashes -r requirements/production.txt

COPY pyproject.toml README.md manage.py ./
COPY src/ src/
RUN pip install --no-cache-dir --no-deps . \
    && DJANGO_SETTINGS_MODULE=allelefounder.config.settings.base \
       DJANGO_SECRET_KEY=build-only-not-a-secret \
       POSTGRES_DB=unused \
       POSTGRES_USER=unused \
       POSTGRES_PASSWORD=unused \
       POSTGRES_HOST=localhost \
       python manage.py collectstatic --noinput \
    && chown -R allelefounder:allelefounder /app

USER 10001:10001
EXPOSE 8000

CMD ["gunicorn", "allelefounder.config.wsgi:application", "--bind=0.0.0.0:8000", "--workers=2", "--error-logfile=-"]
