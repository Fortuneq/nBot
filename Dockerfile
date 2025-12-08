# Multi-stage build для оптимизации размера образа

FROM python:3.11-slim as builder

# Установка build зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Создание виртуального окружения
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# Финальный образ
FROM python:3.11-slim

# Создание непривилегированного пользователя
RUN useradd -m -u 1000 botuser && \
    mkdir -p /app && \
    chown -R botuser:botuser /app

WORKDIR /app

# Копирование виртуального окружения из builder
COPY --from=builder /opt/venv /opt/venv

# Копирование файлов приложения
COPY --chown=botuser:botuser bot.py .
COPY --chown=botuser:botuser .env .

# Переключение на непривилегированного пользователя
USER botuser

# Активация виртуального окружения
ENV PATH="/opt/venv/bin:$PATH"

# Установка переменных окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Запуск приложения
CMD ["python", "bot.py"]
