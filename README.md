# Edutrack

Платформа обмена знаниями — фронтенд и бэкенд в одном проекте.

## Структура

```
edutrack/
├── app/              # FastAPI бэкенд
│   ├── routers/      # auth, users, lessons, matches, challenges, leaderboard
│   ├── models/       # SQLAlchemy модели
│   ├── schemas/      # Pydantic схемы
│   └── core/         # database, security, config
├── static/           # Фронтенд (index.html)
├── migrations/       # Alembic
├── Dockerfile
└── docker-compose.yml
```

## Запуск через Docker (рекомендуется)

```bash
docker-compose up --build
```

Открой браузер: **http://localhost:8000**

API документация: **http://localhost:8000/api/docs**

## Запуск локально (без Docker)

```bash
# 1. Установи зависимости
pip install -r requirements.txt

# 2. Создай .env
cp .env.example .env
# Отредактируй DATABASE_URL под свою БД

# 3. Запусти
uvicorn app.main:app --reload --port 8000
```

## Как это работает

FastAPI отдаёт фронтенд из папки `static/` на маршруте `/`.  
Все API-запросы идут на тот же сервер по префиксу `/api/`.  
CORS настраивать не нужно — всё на одном домене.

## Переменные окружения

| Переменная | По умолчанию | Описание |
|---|---|---|
| `DATABASE_URL` | `postgresql://...` | Строка подключения к PostgreSQL |
| `SECRET_KEY` | `change-this...` | Секрет для JWT токенов |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Время жизни access токена |
| `INITIAL_SKILL_COINS` | `100` | Стартовый бонус при регистрации |
