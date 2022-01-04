from django import forms
from tracer import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django_redis import get_redis_connection
import random
from utils.send_sms import send_sms
from utils import encrypt
from tracer.forms.bootstrap import BootstrapForm

phone_regex = RegexValidator(
       regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")


class RegisterForm(BootstrapForm, forms.ModelForm):
    
    # mobile_phone = forms.CharField(label='Mobile phone', validators=[
    #                               RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', 'Malformed phone number'), ])
  
    password = forms.CharField(label='password', 
                               min_length=8, 
                               max_length=16,
                               error_messages={
                                   'min_length': 'Password must be at least 8 characters long.', 
                                   'max_length': 'Password cannot be longer than 16 characters.'
                                },
                               widget=forms.PasswordInput())
    
    confirm_password = forms.CharField(label='confirm password', 
                                       min_length=8,
                                       max_length=16,
                                       error_messages={
                                           'min_length': 'Repeated password must be at least 8 characters long.',
                                           'max_length': 'Repeated password cannot be longer than 16 characters.'
                                       },
                                       widget=forms.PasswordInput())
    
    mobile_phone = forms.CharField(
        validators=[phone_regex], max_length=17, label='Mobile phone')
    
    code = forms.CharField(label='code', widget=forms.TextInput())
    
    class Meta:
        model = models.UserInfo
        # the order of fields in the form is matter, first defined will be firstly verified
        fields = ['username','email','password', 'confirm_password', 'mobile_phone', 'code']
        
            
    def clean_username(self):
        username = self.cleaned_data['username']
        exists = models.UserInfo.objects.filter(username=username).exists()
        if exists:
            raise ValidationError('Username already exists')
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']
        exists = models.UserInfo.objects.filter(email=email).exists()
        if exists:
            raise ValidationError('Email already exists')
        return email
    
    def clean_password(self):
        password = self.cleaned_data['password']
        return encrypt.md5(password)
    
    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = encrypt.md5(self.cleaned_data['confirm_password'])
        if password != confirm_password:
            raise ValidationError('Password does not match')
        return confirm_password
    
    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exists:
            raise ValidationError('Mobile phone already exists')
        return mobile_phone
    
    def clean_code(self):
        code = self.cleaned_data['code']
        mobile_phone = self.cleaned_data.get('mobile_phone')
        
        if not mobile_phone:
            return code
        
        conn = get_redis_connection()
        redis_code = conn.get(mobile_phone)
        if not redis_code:
            raise ValidationError('Invalid code or expired, please try again')
        
        redis_str_code = redis_code.decode('utf-8')
        
        if code.strip() != redis_str_code:
            raise ValidationError('Invalid code, please try again')
            
        return code
    
class SendSmsForm(forms.Form):
    mobile_phone = forms.CharField(
        validators=[phone_regex], max_length=17, label='Mobile phone')
    
    # get the request object from the view by rewritting the init method
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
    
    def clean_mobile_phone(self):
        """verify mobile phone"""
        mobile_phone = self.cleaned_data['mobile_phone']
        
        # check if the parameter 'tpl' is right or not tpl in [register, login]
        tpl = self.request.GET.get('tpl')
        if tpl not in ['register', 'login']:
            raise ValidationError('Invalid tpl parameter')
        
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if tpl == 'login':
            if not exists:
                raise ValidationError('Mobile phone does not exist')
        else:
            if exists:
                raise ValidationError('Mobile phone already exists')
        
        # check if the sms was sent successfully
        code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        
        send_result = send_sms(mobile_phone, tpl, code)
                
        if send_result.status != 'sent':
            raise ValidationError(
                f'Sending sms failed: {send_result.error_message}')
            # self.add_error('mobile_phone', 'Sending sms failed')
        
        # save the code to the redis cache
        conn = get_redis_connection()
        conn.set(mobile_phone, code, ex=60)
            
        
        return mobile_phone
    
    
class LoginSmsForm(BootstrapForm, forms.Form):
    mobile_phone = forms.CharField(
        validators=[phone_regex], max_length=17, label='Mobile phone')

    code = forms.CharField(label='code', widget=forms.TextInput())

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        # = models.UserInfo.objects.filter(mobile_phone=mobile_phone).first()
        
        if not exists:
            raise ValidationError('Mobile phone already exists')
        return mobile_phone

    def clean_code(self):
        code = self.cleaned_data['code']
        mobile_phone = self.cleaned_data.get('mobile_phone')

        if not mobile_phone:
            return code

        conn = get_redis_connection()
        redis_code = conn.get(mobile_phone)
        if not redis_code:
            raise ValidationError('Invalid code or expired, please try again')

        redis_str_code = redis_code.decode('utf-8')

        if code.strip() != redis_str_code:
            raise ValidationError('Invalid code, please try again')

        return code


class LoginForm(BootstrapForm, forms.Form):
    email_or_phone = forms.CharField(label='Email or Mobil phone')
    password = forms.CharField(label='password', widget=forms.PasswordInput())
    code = forms.CharField(label='image code')
    
    # get the request object from the view by rewritting the init method
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        
        # from request get session and then get image code
        session_code = self.request.session.get('image_code')
        if not session_code:
            raise ValidationError('Image code is expired, please try again')
        
        if code.strip().lower() != session_code.lower():
            raise ValidationError('The image code is wrong, please try again')
        
        return code
    
    def clean_password(self):
        password = self.cleaned_data['password']
        return encrypt.md5(password)
