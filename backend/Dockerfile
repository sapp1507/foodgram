FROM python:3.8-slim-buster

WORKDIR /app

COPY backend/requirements.txt .

RUN pip install -r ./requirements.txt --upgrade pip

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

COPY backend/ .

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000"]