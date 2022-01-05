from django.db import models

# Create your models here.
class UserInfo(models.Model):
    username = models.CharField(verbose_name='Username', max_length=100,unique=True, db_index=True)
    email = models.EmailField(verbose_name='Email',
                              unique=True, max_length=100, db_index=True)
    mobile_phone = models.CharField(
        verbose_name='MobilePhone', max_length=17, db_index=True)
    # mobile_phone = PhoneNumberField(null=False, blank=False, unique=True)
    password = models.CharField(verbose_name='Password', max_length=100)