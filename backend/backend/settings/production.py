import os

from dotenv import load_dotenv

from .base import *

load_dotenv()

DEBUG = True

ALLOWED_HOSTS += [
    'sapp.tk',
]

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME', default='db'),
        'USER': os.getenv('POSTGRES_USER', default='user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', default='password'),
        'HOST': os.getenv('DB_HOST', default='127.0.0.1'),
        'PORT': os.getenv('DB_PORT', default=5432),
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, 'backend_static')
