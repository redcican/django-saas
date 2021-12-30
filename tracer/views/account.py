from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from tracer.forms.account import RegisterForm, SendSmsForm

def register(request):
    form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def send_sms(request):
    """
    Send sms
    """
    form = SendSmsForm(request, data=request.GET)
    if form.is_valid():
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'errors': form.errors})