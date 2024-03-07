FROM python:3.12

COPY . /app
WORKDIR /app

RUN pip install poetry && poetry install --with=simulator
