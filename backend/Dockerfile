FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . /app

# Указываем переменные окружения (можно переопределить при запуске)
ENV PYTHONUNBUFFERED=1

# Команда запуска
CMD ["sh", "-c", "python3 manage.py migrate && python3 -u manage.py runserver 0.0.0.0:8000"]
