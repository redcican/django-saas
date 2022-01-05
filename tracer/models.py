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
    
    
class PricePolicy(models.Model):
    category_choices = (
        (1, 'Free'),
        (2, 'Charge'),
        (3, 'Other')
    )
    category = models.SmallIntegerField(verbose_name='Charge Type', default=2, choices=category_choices)
    title = models.CharField(verbose_name='Title', max_length=32)
    price = models.PositiveIntegerField(verbose_name='Price')
    
    project_num = models.PositiveIntegerField(verbose_name='Project Number')
    project_member = models.PositiveIntegerField(verbose_name='Project Member')
    project_space = models.PositiveIntegerField(verbose_name='Single Project Space')
    per_file_size = models.PositiveIntegerField(verbose_name='Per File Size (M)')
    
    create_datetime = models.DateTimeField(verbose_name='Create Datetime', auto_now_add=True)
    
    
class Transaction(models.Model):
    status_choices = (
        (1, 'Unpaid'),
        (2, 'Paid'),
    )
    
    status = models.SmallIntegerField(verbose_name='Status', choices=status_choices)
    
    order = models.CharField(verbose_name='Order Number', max_length=128, unique=True)
    user = models.ForeignKey(to='UserInfo', verbose_name='User', on_delete=models.CASCADE)
    price_policy = models.ForeignKey(to='PricePolicy', verbose_name='Price Policy', on_delete=models.CASCADE)
    
    count = models.IntegerField(verbose_name='Count (Year)', help_text='Zero means forever')
    
    price = models.IntegerField(verbose_name='Actually Paid Price')
    
    start_datetime = models.DateTimeField(verbose_name='Start Datetime', null=True, blank=True)
    end_datetime = models.DateTimeField(verbose_name='End Datetime', null=True, blank=True)
    
    create_datetime = models.DateTimeField(verbose_name='Create Datetime', auto_now_add=True)