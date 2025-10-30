#!/bin/bash

echo "=== Тестирование микросервисов URL Shortener ==="
echo ""

echo "1. Проверка статуса контейнеров..."
docker-compose ps
echo ""

echo "2. Health Check основного сервиса..."
curl -s http://localhost/health | python -m json.tool || echo "Сервис не доступен"
echo ""

echo "3. Health Check через прямой порт (5000)..."
curl -s http://localhost:5000/health | python -m json.tool || echo "Сервис не доступен"
echo ""

echo "4. Health Check Analytics Service (5001)..."
curl -s http://localhost:5001/health | python -m json.tool || echo "Сервис не доступен"
echo ""

echo "5. Health Check Notification Service (5002)..."
curl -s http://localhost:5002/health | python -m json.tool || echo "Сервис не доступен"
echo ""

echo "=== Тестирование завершено ==="
echo ""
echo "Откройте в браузере: http://localhost"
echo "Для просмотра логов: docker-compose logs -f"

