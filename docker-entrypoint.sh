#!/bin/sh

echo "Collect static"
python manage.py collectstatic --no-input

echo "Migrate"
python manage.py migrate

echo "Runserver"
gunicorn api_yamdb.wsgi:application --bind 0.0.0.0:8000