# --- build stage ---
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Сначала — только requirements.txt, чтобы кэшировать слой с зависимостями
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Затем — весь код проекта
COPY . .

# Непривилегированный пользователь
RUN useradd --create-home --shell /bin/bash appuser \
 && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Применяем миграции и запускаем uvicorn
CMD ["sh", "-c", "aerich upgrade && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
