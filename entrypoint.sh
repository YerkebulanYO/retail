#!/bin/sh

set -e

echo "Применение миграций..."
python3 manage.py migrate

echo "Запуск сервера Django..."
exec python3 manage.py runserver 0.0.0.0:8091
