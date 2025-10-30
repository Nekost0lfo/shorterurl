FROM python:3.9-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование приложения
COPY . .

# Создание директорий для данных (если нужно)
VOLUME ["/app/data"]

EXPOSE 5000

# Запуск приложения
CMD ["python", "app.py"]