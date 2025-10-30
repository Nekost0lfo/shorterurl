# URL Shortener - Микросервисная архитектура с Docker

Проект представляет собой систему сокращения URL на основе микросервисной архитектуры с использованием Docker и Docker Swarm для оркестрации.

## Архитектура

Проект состоит из трех основных микросервисов:

1. **URL Shortener** (Порт 5000) - Основной сервис для создания и редиректа коротких ссылок
2. **Analytics Service** (Порт 5001) - Сервис аналитики для отслеживания кликов
3. **Notification Service** (Порт 5002) - Сервис уведомлений о создании новых ссылок

Все сервисы проходят через **NGINX** (Порт 80), который выступает в роли reverse proxy и load balancer.

## Требования

- Docker 20.10+
- Docker Compose 1.29+
- (Опционально) Docker Swarm для production развертывания

## Структура проекта

```
.
├── url-shortener/          # Основной микросервис
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── static/
│   └── templates/
├── analytics-service/      # Сервис аналитики
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── notification-service/   # Сервис уведомлений
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── nginx/                  # NGINX конфигурация
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml      # Docker Compose для разработки
├── docker-compose-swarm.yml # Docker Swarm конфигурация
├── deploy-swarm.sh         # Скрипт развертывания Swarm
└── README.md
```

## Быстрый старт

### Запуск с Docker Compose

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd ShorterURL
```

2. Запустите все сервисы:
```bash
docker-compose up -d --build
```

3. Проверьте статус сервисов:
```bash
docker-compose ps
```

4. Откройте в браузере:
```
http://localhost
```

### Остановка сервисов

```bash
docker-compose down
```

Для удаления volumes (баз данных):
```bash
docker-compose down -v
```

## Развертывание с Docker Swarm

### Инициализация Swarm

```bash
docker swarm init
```

### Развертывание стека

Используйте готовый скрипт:
```bash
chmod +x deploy-swarm.sh
./deploy-swarm.sh
```

Или вручную:
```bash
docker stack deploy -c docker-compose-swarm.yml url-shortener-stack
```

### Управление стеком

Просмотр сервисов:
```bash
docker service ls
```

Просмотр логов:
```bash
docker service logs url-shortener-stack_nginx
docker service logs url-shortener-stack_url-shortener
```

Масштабирование сервиса:
```bash
docker service scale url-shortener-stack_url-shortener=3
```

Удаление стека:
```bash
docker stack rm url-shortener-stack
```

## API Endpoints

### URL Shortener Service

- `GET /` - Главная страница с интерфейсом
- `POST /shorten` - Создание короткой ссылки
  ```json
  {
    "url": "https://example.com"
  }
  ```
- `GET /<short_code>` - Редирект на оригинальный URL
- `GET /stats/<short_code>` - Получение статистики
- `GET /health` - Проверка здоровья сервиса

### Analytics Service

- `POST /track` - Отслеживание клика
- `GET /analytics/<short_code>` - Получение аналитики
- `GET /health` - Проверка здоровья сервиса

### Notification Service

- `POST /notify` - Отправка уведомления
- `GET /notifications` - Получение списка уведомлений
- `GET /health` - Проверка здоровья сервиса

## NGINX Маршрутизация

- `/` → URL Shortener Service
- `/api/analytics/*` → Analytics Service
- `/api/notifications/*` → Notification Service
- `/health` → Health check
- `/static/*` → Статические файлы

## Переменные окружения

### URL Shortener
- `FLASK_ENV` - Режим Flask (development/production)
- `ANALYTICS_SERVICE_URL` - URL сервиса аналитики
- `NOTIFICATION_SERVICE_URL` - URL сервиса уведомлений

## Базы данных

Каждый сервис использует SQLite для хранения данных:
- `url-shortener.db` - URL Shortener Service
- `analytics.db` - Analytics Service  
- `notifications.db` - Notification Service

Данные сохраняются в Docker volumes для персистентности.

## Мониторинг и отладка

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f url-shortener
```

### Проверка здоровья

```bash
curl http://localhost/health
```

### Вход в контейнер

```bash
docker-compose exec url-shortener bash
```

## Разработка

### Локальная разработка

Для разработки отдельных сервисов:

```bash
cd url-shortener
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Добавление новых сервисов

1. Создайте директорию для сервиса
2. Добавьте Dockerfile
3. Обновите docker-compose.yml
4. Обновите nginx.conf для маршрутизации

## Production рекомендации

1. **Безопасность:**
   - Используйте HTTPS (добавьте SSL сертификаты)
   - Настройте firewall
   - Используйте секреты Docker для чувствительных данных

2. **Производительность:**
   - Используйте Docker Swarm или Kubernetes для оркестрации
   - Настройте мониторинг (Prometheus, Grafana)
   - Настройте логирование (ELK Stack)

3. **Масштабирование:**
   - Увеличьте количество replicas в docker-compose-swarm.yml
   - Используйте внешнюю БД (PostgreSQL, MySQL) вместо SQLite
   - Добавьте Redis для кэширования

4. **Резервное копирование:**
   - Настройте автоматическое резервное копирование volumes
   - Используйте managed database services

## Troubleshooting

### Проблема: Сервисы не могут подключиться друг к другу

**Решение:** Проверьте, что все сервисы находятся в одной сети `url-shortener-network`

### Проблема: NGINX возвращает 502 Bad Gateway

**Решение:** 
1. Проверьте, что все сервисы запущены: `docker-compose ps`
2. Проверьте логи: `docker-compose logs nginx`

### Проблема: Данные теряются после перезапуска

**Решение:** Убедитесь, что volumes правильно настроены и не удалялись при `docker-compose down -v`

## Лицензия

MIT

## Автор

URL Shortener Project

## Контакты

Для вопросов и предложений создайте issue в репозитории.

