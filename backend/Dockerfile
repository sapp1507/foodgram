FROM python:3.8-slim-buster

WORKDIR /app

COPY backend/requirements.txt .

RUN pip install -r ./requirements.txt --upgrade pip

COPY backend/ .

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000"]