from django.shortcuts import render
from tracer.forms.account import RegisterForm

def register(request):
    form = RegisterForm()
    return render(request, 'register.html', {'form': form})