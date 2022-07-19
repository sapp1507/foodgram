FROM python:3.8-slim

WORKDIR /app

COPY ./requirements.txt .

RUN pip install -r ./requirements.txt --no-cache-dir --upgrade pip

COPY ./ .

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:0"]