from django.urls import path

from .views import account

app_name = 'tracer'

urlpatterns = [
    path('register/', account.register, name='register'),
]
