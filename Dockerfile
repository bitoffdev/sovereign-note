FROM python:3.8-slim

RUN set -x && \
    python -m pip install pip==22.0.3 && \
    pip install poetry==1.1.12

WORKDIR /src

COPY pyproject.toml poetry.lock ./

RUN set -x && \
    poetry install

COPY . .

