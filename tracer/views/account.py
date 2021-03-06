from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from tracer import models
from tracer.forms.account import LoginForm, RegisterForm, SendSmsForm, LoginSmsForm
from utils.image_code import generate_image_code
from io import BytesIO
import uuid
import datetime

def register(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})
    
    form = RegisterForm(data=request.POST)
    if form.is_valid():
        instance = form.save()
        """
        policy_object = models.PricePolicy.objects.filter(
            category=1, title='Personal Free').first()
        """
        policy_object=models.PricePolicy.objects.create(
            category=1,
            title="Personal Free",
            price=0,
            project_num=3,
            project_member=2,
            project_space=20,
            per_file_size=5
        )
        # 创建默认交易记录，当创建用户时自动创建
        models.Transaction.objects.create(
            status=2,
            order=str(uuid.uuid4()),
            user=instance, 
            price_policy=policy_object,
            count = 0,
            price = 0,
            start_datetime = datetime.datetime.now()
        )
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
        mobile_phone = form.cleaned_data['mobile_phone']
        
        # write the user name into session
        user_object = models.UserInfo.objects.filter(mobile_phone=mobile_phone).first()
        request.session['user_id'] = user_object.id
        request.session.set_expiry(60 * 60 * 24 * 14)
        # return redirect('tracer:index')
        return JsonResponse({'status': True, 'data': '/index/'})
    
    return JsonResponse({'status': False, 'errors': form.errors})

def login(request):
    """use username and password"""
    
    if request.method == 'GET':
        form = LoginForm(request)
        return render(request, 'login.html', {'form': form})
    
    form = LoginForm(request, data=request.POST)
    if form.is_valid():
        email_or_phone = form.cleaned_data['email_or_phone']
        password = form.cleaned_data['password']
        
        from django.db.models import Q
        user_object = models.UserInfo.objects.filter(Q(mobile_phone=email_or_phone) | Q(email=email_or_phone)).filter(password=password).first()
        
        if user_object:
            request.session['user_id'] = user_object.id
            request.session.set_expiry(60 * 60 * 24 * 14)
            return redirect('tracer:index')
        form.add_error('email_or_phone', 'Invalid username or password')

    return render(request, 'login.html', {'form': form})

def image_code(request):
    """
    generate the url for image code
    """

    image_object, code = generate_image_code()
    # save image code to session
    request.session['image_code'] = code
    # set expired time to 60a
    request.session.set_expiry(60)
    
    stream = BytesIO()
    image_object.save(stream, 'png')
    return HttpResponse(stream.getvalue())

def logout(request):
    """
    logout
    """
    request.session.flush()
    return redirect('tracer:index')