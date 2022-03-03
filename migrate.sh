#!/bin/bash

SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-"cican17@gmail.com"}
SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD:-"1228"}
SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME0:-"admin"}
cd /app/

/opt/venv/bin/python manage.py migrate --run-syncdb --noinput
/opt/venv/bin/python manage.py collectstatic --no-input --clear
/opt/venv/bin/python manage.py wait_for_db
/opt/venv/bin/python scripts/create_price_policy.py

/opt/venv/bin/python manage.py createsuperuser2 --username $SUPERUSER_USERNAME --password $SUPERUSER_PASSWORD --noinput --email $SUPERUSER_EMAIL || true
