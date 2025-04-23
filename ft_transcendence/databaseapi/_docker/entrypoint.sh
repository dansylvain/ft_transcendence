#!/bin/bash

python3 manage.py makemigrations databaseapi_app
python3 manage.py migrate

# ! Init users DB populate
python3 manage.py runscript init_users

python3 manage.py makemigrations databaseapi_app
python3 manage.py makemigrations
python3 manage.py migrate

if [ "${env}" = "prod" ]; then \
    mkdir -p /app/staticfiles && chmod -R 777 /app/staticfiles; \
    python3 manage.py collectstatic --noinput; \
    uvicorn ${name}.asgi:application --host 0.0.0.0 --port ${port}; \
else \
    python3 ./manage.py runserver 0.0.0.0:${port}; \
fi

exec "$@"