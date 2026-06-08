# 🧠 API сервиса викторин

REST API для создания и прохождения тестов/викторин.

## Стек

- **FastAPI** + Swagger (`/docs`)
- **PostgreSQL 16** (изолирована от внешних соединений)
- **SQLAlchemy 2.0** (async)
- **Alembic** (миграции)
- **JWT** (python-jose) — авторизация по токену
- **Docker Compose** — сервис + БД в одной сети

## Сущности

| Сущность | Описание |
|---|---|
| `User` | Пользователь (username, пароль bcrypt, token_version для logout) |
| `Test` | Тест/викторина (название, описание, видимость, владелец) |
| `Question` | Вопрос теста (текст, привязан к тесту) |
| `Answer` | Вариант ответа (текст, флаг правильности, привязан к вопросу) |
| `UserAnswer` | Ответ пользователя на вопрос (связка user + question + answer) |

## Эндпоинты

### Auth
| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/auth/register` | Регистрация (username + password + confirm_password) |
| `POST` | `/auth/login` | Вход, получение JWT-токена |
| `POST` | `/auth/logout` | Выход, аннулирование токена |

### Tests
| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/tests/` | Создать тест (название + описание) |
| `PATCH` | `/tests/{id}/visibility` | Скрыть/раскрыть тест (только владелец) |

### Questions
| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/tests/{id}/questions` | Загрузить вопрос + массив вариантов ответов |
| `GET` | `/tests/{id}/questions` | Список вопросов теста |
| `PUT` | `/questions/{id}` | Изменить вопрос |
| `DELETE` | `/questions/{id}` | Удалить вопрос |

### Answers
| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/questions/{id}/answers` | Список ответов на вопрос |
| `POST` | `/questions/{id}/answers` | Добавить вариант ответа (с флагом `is_correct`) |
| `PUT` | `/answers/{id}` | Изменить ответ |
| `DELETE` | `/answers/{id}` | Удалить ответ |

### Прохождение
| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/tests/{id}/pass` | Ответить на вопрос теста |
| `GET` | `/tests/{id}/results` | Результаты: свои или всех (для владельца) |

Авторизация: `Authorization: Bearer <token>` для всех эндпоинтов, кроме регистрации и логина.

## Быстрый старт

```bash
make up
```

Swagger: http://localhost:8000/docs

### Makefile

| Команда | Действие |
|---|---|
| `make up` | Запустить контейнеры |
| `make down` | Остановить контейнеры |
| `make restart` | Перезапустить |
| `make logs` | Логи |
| `make migrate` | Накатить миграции |
| `make rollback` | Откатить последнюю миграцию |
| `make shell` | Python shell в контейнере |

## Архитектура

Трёхслойная:

```
app/api/      → HTTP, валидация (Pydantic)
app/services/ → Бизнес-логика, запросы к БД
app/models/   → SQLAlchemy ORM
```
