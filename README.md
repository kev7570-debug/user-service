# User Service

Учебный дипломный проект

Асинхронный REST API для хранения данных пользователей с аутентификацией
через cookie и разграничением доступа между пользователем и администратором.

Стек: Python 3.11, FastAPI, Tortoise ORM, PostgreSQL, Aerich, pytest, Docker.

## Возможности

- вход по email и паролю, хранение паролей в виде Argon2-хеша;
- отзываемые серверные сессии: клиент получает случайный токен, в БД хранится
  только его SHA-256-хеш;
- получение и изменение собственных данных;
- постраничный просмотр кратких данных пользователей;
- административный CRUD пользователей и справочник городов;
- единая JSON-обработка ожидаемых и непредвиденных ошибок;
- Swagger UI `/docs` и ReDoc `/redoc`;
- автоматические тесты и контроль покрытия не ниже 75%.

## Структура

```text
app/
├── api/                 # маршруты, зависимости доступа и ответы OpenAPI
├── core/                # безопасность и обработка исключений
├── models/              # User, City, Session
├── schemas/             # Pydantic-схемы запросов и ответов
├── scripts/             # создание первого администратора
├── tests/               # API- и permission-тесты
├── config.py            # настройки из окружения
├── database.py          # конфигурация Tortoise ORM
└── main.py              # фабрика и экземпляр FastAPI-приложения
migrations/              # миграции Aerich
docs/                    # спецификация API (приложение к ТЗ)
.github/workflows/       # CI
```

## Запуск через Docker

```bash
cp .env.example .env
docker compose up --build
```

При запуске контейнер приложения применяет `aerich upgrade`. API доступно на
`http://localhost:8000`, Swagger — на `http://localhost:8000/docs`.

Первого администратора можно создать интерактивной командой:

```bash
docker compose exec app python -m app.scripts.create_admin \
  --email admin@example.com --first-name Admin --last-name User
```

PostgreSQL намеренно не публикует порт наружу. Для локального подключения к БД
можно временно добавить `ports: ["5432:5432"]` сервису `db`.

## Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate             # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Для запуска вне Docker измените `DB_HOST=db` на `DB_HOST=localhost`, затем:

```bash
aerich upgrade
uvicorn app.main:app --reload
```

## Тесты и качество кода

```bash
ruff check .
ruff format --check .
python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=75
```

Тесты используют отдельную SQLite in-memory базу и фабрику приложения без
production-подключения. GitHub Actions повторяет линтер, тесты и сборку образа.

## Настройки cookie

Для localhost используется `COOKIE_SECURE=False`. При использовании HTTPS
в `.env` устанавливается:

```env
COOKIE_SECURE=True
COOKIE_SAMESITE=lax
```

Cookie имеет флаги `HttpOnly`, `SameSite`, ограниченный срок жизни и `Path=/`.
Logout удаляет cookie клиента и соответствующую запись сессии в БД.

## Принятые проектные решения

1. `LoginModel.login` трактуется как email. Отдельного username в исходных
   моделях создания пользователя нет.
2. Пользователь редактирует только свои данные по пути `/users/current`,
   как описано в спецификации (приложение к ТЗ).
3. В `PATCH /private/users/{pk}` поле `id` в теле запроса обязательно и
   должно совпадать с `pk` из URL. При несовпадении — 400.
4. Необязательные при создании поля допускают `null` и в ответах — иначе
   новый пользователь без отчества, телефона или города не прошёл бы
   сериализацию.
5. Параметры пагинации ограничены: `page >= 1`, `1 <= size <= 100` — защита
   от выкачивания всей базы одним запросом.
6. Email нормализуется к нижнему регистру и проверяется на уникальность.
7. Добавлен скрытый из OpenAPI endpoint `/health` для Docker healthcheck.
8. Массив подсказок городов называется `hint.city` — так в спецификации.

## Секреты и .env

Файл `.env` содержит пароль от БД и в репозиторий не коммитится.
Шаблон переменных — в `.env.example`.

## Автор

Elena Kashina
