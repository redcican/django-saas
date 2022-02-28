"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
from dotenv import load_dotenv



import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-x@r^w#sozd_cj=78i=dfnx=)up$b&r19vq)=50_8rvl^wh4g5r'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = str(os.getenv('DEBUG')) == '1'

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tracer',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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

redis_host = os.getenv('REDIS_HOST_IP')
redis_ip = os.getenv('REDIS_HOST_PORT')
redis_password = os.getenv('REDIS_PASSWORD')
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis:://{redis_host}:{redis_ip}",  # 安装redis的主机的 IP 和 端口
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
postgres_database_name = os.getenv('POSTGRES_DATABASE_NAME')
postgres_user_name = os.getenv('POSTGRES_USER_NAME')
postgres_password = os.getenv('POSTGRES_PASSWORD')
postgres_host = os.getenv('POSTGRES_HOST')
postgres_port = os.getenv('POSTGRES_PORT')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': postgres_database_name,
        'USER': postgres_user_name,
        'PASSWORD': postgres_password,
        'HOST': postgres_host,
        'PORT': postgres_port
    }
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

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# TENCENT credentials
TENCENT_COS_SECRET_ID = os.getenv('TENCENT_COS_SECRET_ID')
TENCENT_COS_SECRET_KEY = os.getenv('TENCENT_COS_SECRET_KEY')
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
    "/price/"
]

X_FRAME_OPTIONS = 'SAMEORIGIN'
