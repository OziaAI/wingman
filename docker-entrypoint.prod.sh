#!/bin/sh

poetry run python3 manage.py migrate
poetry run uvicorn wingman.asgi:application --proxy-headers --host 0.0.0.0 --port 8000 --forwarded-allow-ips='*'
