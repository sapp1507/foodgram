FROM python:3.8

WORKDIR /app

COPY backend/requirements.txt .

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

RUN pip install -r ./requirements.txt --upgrade pip



COPY backend/ .

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000"]