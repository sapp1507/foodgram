FROM python:3.8-slim

WORKDIR /app

COPY backend/requirements.txt .

RUN pip install -r ./requirements.txt --upgrade pip
RUN pip install psycopg2-binary

COPY backend/ .

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000"]