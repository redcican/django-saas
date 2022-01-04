from django.urls import path

from .views import account
from .views import home

app_name = 'tracer'

urlpatterns = [
    path('register/', account.register, name='register'),
    path('login/sms/', account.login_sms, name='login_sms'),
    path('login/', account.login, name='login'),
    path('imgae/code&', account.image_code, name='image_code'),
    path('send/sms/', account.send_sms, name='send_sms'),
    
    path('index/', home.index, name='index'),
]
