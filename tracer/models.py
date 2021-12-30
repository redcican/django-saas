from django.db import models
from django.core.validators import RegexValidator

# Create your models here.
class UserInfo(models.Model):
    username = models.CharField(verbose_name='Username', max_length=100)
    email = models.EmailField(verbose_name='Email', max_length=100)
    mobile_phone = models.CharField(verbose_name='MobilePhone', max_length=17)
    # mobile_phone = PhoneNumberField(null=False, blank=False, unique=True)
    password = models.CharField(verbose_name='Password', max_length=100)