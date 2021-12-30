from django.urls import path

from .views import account

app_name = 'tracer'

urlpatterns = [
    path('register/', account.register, name='register'),
    path('send/sms/', account.send_sms, name='send_sms'),
]
