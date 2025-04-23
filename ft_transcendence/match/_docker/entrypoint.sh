#!/bin/bash

# Make the scripts fails if any command fails
set -e

# ! IMPORTANT : You need to NOT migrate this container.

if [ "${env}" = "prod" ]; then \
	mkdir -p /app/staticfiles && chmod -R 777 /app/staticfiles; \
	python3 manage.py collectstatic --noinput; \
fi

daphne -b 0.0.0.0 -p ${port} ${name}.asgi:application

exec "$@"