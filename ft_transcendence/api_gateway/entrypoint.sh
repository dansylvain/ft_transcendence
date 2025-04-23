#!/bin/bash

uvicorn ${name}.asgi:application --host 0.0.0.0 --port ${port}; \

exec "$@"
