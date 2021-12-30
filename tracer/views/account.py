from django.http.response import HttpResponse
from django.shortcuts import render
from tracer.forms.account import RegisterForm

def register(request):
    form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def send_sms(request):
    """
    Send sms
    """
    print(request.GET)
    return HttpResponse('<h1>Send sms</h1>')