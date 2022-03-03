"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path

import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY','django-insecure-x@r^w#sozd_cj=78i=dfnx=)up$b&r19vq)=50_8rvl^wh4g5r')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = str(os.environ.get('DEBUG')) == '1'

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    "whitenoise.runserver_nostatic",
    'django.contrib.staticfiles',
    'tracer',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'tracer.middleware.auth.AuthMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

redis_host = os.environ.get('REDIS_HOST')
redis_port = os.environ.get('REDIS_HOST_PORT')
redis_password = os.environ.get('REDIS_PASSWORD')
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis:://{redis_host}:{redis_port}/0",  # 安装redis的主机的 IP 和 端口
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 1000,
                "encoding": 'utf-8'
            },
            "PASSWORD": redis_password  # redis密码
        }
    }
}

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
postgres_database_name = os.environ.get('POSTGRES_DB')
postgres_user_name = os.environ.get('POSTGRES_USER_NAME')
postgres_password = os.environ.get('POSTGRES_PASSWORD')
postgres_host = os.environ.get('POSTGRES_HOST')
postgres_port = os.environ.get('POSTGRES_PORT')

DB_IGNORE_SSL=os.environ.get('DB_IGNORE_SSL') == 'true'

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.postgresql_psycopg2', (local)
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': postgres_database_name,
        'USER': postgres_user_name,
        'PASSWORD': postgres_password,
        'HOST': postgres_host,
        'PORT': postgres_port
    }
}

if not DB_IGNORE_SSL:
    DATABASES['default']['OPTIONS'] = {
        'sslmode': 'require'
    }

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Twilio credentials
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

# TENCENT credentials
TENCENT_COS_SECRET_ID = os.environ.get('TENCENT_COS_SECRET_ID')
TENCENT_COS_SECRET_KEY = os.environ.get('TENCENT_COS_SECRET_KEY')
# TENCENT_COS_REGION = os.getenv('TENCENT_COS_REGION')
# TENCENT_COS_BUCKET = os.getenv('TENCENT_COS_BUCKET')

# ALI PAY SANDBOX
ALIPAY_APPID = "2021000119623291"

ALIPAY_GATEWAY = "https://openapi.alipaydev.com/gateway.do"
ALIPAY_PRIVATE_KEY_PATH = BASE_DIR / 'files' / 'privatekey2048.txt'
ALIPAY_PUBLIC_KEY_PATH = BASE_DIR / 'files' / 'alipay_key.txt'
ALIPAY_NOTIFY_URL = 'http://127.0.0.1:8000/pay/notify/'  # POST
ALIPAY_RETURN_URL = 'http://127.0.0.1:8000/pay/notify/'  # GET


# white list: can be accessed without login
WHITE_REGEX_URL_LIST = [
    "/register/",
    "/login/",
    "/login/sms/",
    "/image/code/",
    "/send/sms/",
    "/index/",
    "/price/",
    "/admin/",
]

X_FRAME_OPTIONS = 'SAMEORIGIN'
