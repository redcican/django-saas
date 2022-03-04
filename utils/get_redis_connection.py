import redis
from django.conf import settings

host = settings.REDIS_HOST
port = settings.REDIS_PORT
password = settings.REDIS_PASSWORD
redis_connection = redis.Redis(host=host, port=port, password=password)