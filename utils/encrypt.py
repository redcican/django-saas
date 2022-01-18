import hashlib
from django.conf import settings
import uuid

def md5(password: str):
    """
    md5 encrypt password
    """
    hash_object = hashlib.md5(settings.SECRET_KEY.encode('utf-8'))
    hash_object.update(password.encode('utf-8'))
    return hash_object.hexdigest()


def uid(string: str):
    """generate a random name for image file"""
    data = f"{str(uuid.uuid4())}-{string}"
    return md5(data)