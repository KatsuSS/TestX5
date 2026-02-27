#!/bin/bash
set -e

echo "Ждём пока база данных станет доступна..."
sleep 5

echo "Применяем миграции..."
uv run python /app/src/manage.py migrate --noinput

echo "Собираем статику..."
uv run python /app/src/manage.py collectstatic --noinput

echo "Запускаем сервер..."
exec uv run python /app/src/manage.py runserver 0.0.0.0:8000
