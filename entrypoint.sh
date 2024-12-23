#!/bin/sh

# Ожидаем, пока база данных не станет доступной
until pg_isready -h db -p 5432 -U testuser; do
  echo "Ожидание подключения к PostgreSQL..."
  sleep 2
done

# Применяем миграции
flask db init
flask db migrate
flask db upgrade

# Создаём администратора, если его ещё нет
flask cli_bp create-user --username admin --password adminpass --role admin || true

# Запускаем Celery
celery -A app.tasks.celery worker -B --loglevel=info &
# Запускаем uWSGI
exec uwsgi --ini uwsgi.ini