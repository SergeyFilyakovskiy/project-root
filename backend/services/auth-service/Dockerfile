# auth-service, integration-service, analytics-service,
# manual-input-service, reporting-service, notification-service

FROM python:3.11-slim

# системные зависимости (нужны для psycopg2, weasyprint и др.)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# сначала только зависимости — чтобы кешировался слой
COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# потом копируем код
COPY app/ ./app/

# healthcheck встроенный
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
