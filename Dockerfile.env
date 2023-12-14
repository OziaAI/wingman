FROM python:3.12-alpine3.17

ENV POETRY_VERSION=1.4.2

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /container
COPY . .
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

EXPOSE 8000

ENTRYPOINT [ "poetry", "run", "python3", "manage.py", "runserver" ]
