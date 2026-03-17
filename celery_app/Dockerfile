FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/celery_app/requirements.txt
RUN pip install --no-cache-dir -r /app/celery_app/requirements.txt

# Копирование проекта
COPY . /app/celery_app

# Команда для запуска Celery
CMD ["celery", "-A", "celery_app", "worker", "-l", "INFO", "-c 1"]
