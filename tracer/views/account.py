from django.http.response import JsonResponse
from django.shortcuts import render
from tracer.forms.account import RegisterForm, SendSmsForm, LoginSmsForm

def register(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})
    
    form = RegisterForm(data=request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({'status': True, 'data': '/login/'})
    
    return JsonResponse({'status': False, 'errors': form.errors})

def send_sms(request):
    """
    Send sms
    """
    form = SendSmsForm(request, data=request.GET)
    if form.is_valid():
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'errors': form.errors})

def login_sms(request):
    """
    Login with sms
    """
    if request.method == 'GET':
        form = LoginSmsForm()
        return render(request, 'login_sms.html', {'form': form})
    
    form = LoginSmsForm(data=request.POST)
    if form.is_valid():
        # user = form.cleaned_data['mobile_phone']
        # put user info to session -- TODO
        return JsonResponse({'status': True, 'data': '/index/'})
    
    return JsonResponse({'status': False, 'errors': form.errors})
