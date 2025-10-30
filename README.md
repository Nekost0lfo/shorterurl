# URL Shortener - Микросервисная архитектура с Docker

Проект представляет собой систему сокращения URL на основе микросервисной архитектуры с использованием Docker и Docker Swarm для оркестрации.

## Архитектура

Проект состоит из трех основных микросервисов:

1. **URL Shortener** (Порт 5000) - Основной сервис для создания и редиректа коротких ссылок
2. **Analytics Service** (Порт 5001) - Сервис аналитики для отслеживания кликов
3. **Notification Service** (Порт 5002) - Сервис уведомлений о создании новых ссылок

Все сервисы проходят через **NGINX** (Порт 80), который выступает в роли reverse proxy и load balancer.


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

