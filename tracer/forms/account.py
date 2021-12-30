from django import forms
from django.core.validators import RegexValidator
from tracer import models


class RegisterForm(forms.ModelForm):
    
    mobile_phone = forms.CharField(label='Mobile phone', validators=[
                                   RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', 'Malformed phone number'), ])
    
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
            