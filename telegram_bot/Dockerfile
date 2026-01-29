# Используем официальный образ Python
FROM python:3.11-slim

WORKDIR /app

# Установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . /app

# Команда для запуска бота
CMD ["python3", "-u", "main.py"]
