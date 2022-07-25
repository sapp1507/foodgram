FROM python:3.8-slim-buster AS builder

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY backend/requirements.txt .

RUN pip install -r ./requirements.txt --no-cache-dir --upgrade pip
RUN pip install psycopg2

FROM python:3.8-slim

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY backend/ .

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000"]