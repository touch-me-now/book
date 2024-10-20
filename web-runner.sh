#!/bin/bash

pip install --upgrade pip

echo 'Collecting static files...'
python manage.py collectstatic --no-input

echo 'Making migrations...'
python manage.py makemigrations --no-input
echo 'Migrate...'
python manage.py migrate --no-input

echo 'Filling categories...'
python manage.py loaddata static/fixtures/category_fixtures.json
echo 'Filling books...'
python manage.py loaddata static/fixtures/book_fixtures.json

echo 'Running server...'
gunicorn book_platform.wsgi:application --bind 0.0.0.0:8000

