# FlaskFlow - Система управления транзакциями

FlaskFlow - это веб-приложение на Flask для управления транзакциями с поддержкой JWT-авторизации, Celery для фоновых задач и Swagger для документации API.

## Основные возможности

- 🔐 JWT-авторизация
- 💰 Управление транзакциями (создание, отмена, проверка статуса)
- 👥 Разделение прав (админ/пользователь)
- 📝 Swagger документация API
- 🔄 Фоновые задачи через Celery
- 🐳 Docker контейнеризация

## Технологический стек

- **Backend**: Python 3.10, Flask
- **База данных**: PostgreSQL
- **Очереди**: Redis, Celery
- **Веб-сервер**: Nginx + uWSGI
- **Контейнеризация**: Docker, Docker Compose
- **Документация**: Swagger/OpenAPI

## Быстрый старт

1. Клонируйте репозиторий:

```commandline
git clone https://github.com/anxnas/flaskflow.git
cd flaskflow
```

2. Измените `environment` в `docker-compose.yml`

3. Запустите через Docker Compose:

```commandline
docker-compose build
docker-compose up -d
```


Приложение будет доступно по адресу: http://localhost

## API Endpoints

| Метод | Путь | Описание |
|-------|------|----------|
| POST | /api/auth/login | Авторизация (получение JWT) |
| POST | /api/create_transaction | Создание транзакции |
| POST | /api/cancel_transaction | Отмена транзакции |
| GET | /api/check_transaction | Проверка статуса транзакции |

Полная документация API доступна по адресу: http://localhost/api/docs

## Структура проекта


## Разработка

1. Создайте виртуальное окружение:

```commandline
python -m venv venv
source venv/bin/activate # Linux/macOS
venv\Scripts\activate # Windows
```

2. Установите зависимости:

```commandline
pip install -r requirements.txt
```

3. Запустите миграции:
flask db init
flask db migrate
flask db upgrade

4. Создайте администратора:
```commandline
flask cli_bp create-user --username admin --password adminpass --role admin
```

5. Запустите сервер разработки:

```commandline
python run.py
```


## Тестирование

Запуск тестов:
```commandline
pytest
```

С покрытием кода:
```commandline
pytest --cov=app tests/
```

## Лицензия

MIT License. См. файл [LICENSE](LICENSE) для деталей.

## Автор

Ваше имя - [GitHub](https://github.com/anxnas), [ТГК](https://t.me/anxnas)

## Участие в разработке

1. Fork репозитория
2. Создайте ветку для фичи (`git checkout -b feature/amazing`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в ветку (`git push origin feature/amazing`)
5. Создайте Pull Request