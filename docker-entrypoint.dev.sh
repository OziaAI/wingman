#!/bin/sh

exit_with_missing()
{
    echo "Missing $1, please check if volumes are mounted correctly.";
    exit 1;
}

if ! [ -d /app/project ]; then
    exit_with_missing "project";
fi

cd /app/project;

poetry run python3 manage.py runserver;
