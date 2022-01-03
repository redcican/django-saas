from django import forms
from tracer import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django_redis import get_redis_connection
import random
from utils.send_sms import send_sms


phone_regex = RegexValidator(
       regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")


class RegisterForm(forms.ModelForm):
    
    # mobile_phone = forms.CharField(label='Mobile phone', validators=[
    #                               RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', 'Malformed phone number'), ])

    mobile_phone = forms.CharField(
        validators=[phone_regex], max_length=17, label='Mobile phone')
  
    
    password = forms.CharField(label='password', widget=forms.PasswordInput())
    
    confirm_password = forms.CharField(label='confirm password', widget=forms.PasswordInput())
    
    code = forms.CharField(label='code', widget=forms.TextInput())
    
    class Meta:
        model = models.UserInfo
        fields = ['username','email','password', 'confirm_password', 'mobile_phone', 'code']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = 'Please enter %s' % (field.label,)
            
            
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
        
        if models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists():
            raise ValidationError('Mobile phone already exists')
        
        # check if the sms was sent successfully
        code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        
        send_result = send_sms(mobile_phone, tpl, code)
        
        
        if send_result.status != 'sent':
            raise ValidationError(
                f'Sending sms failed: {send_result.error_message}')
        
        # save the code to the redis cache
        conn = get_redis_connection()
        conn.set(mobile_phone, code, ex=60)
            
        
        return mobile_phone