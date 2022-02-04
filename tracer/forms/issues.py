from django import forms
from tracer.forms.bootstrap import BootstrapForm
from tracer.models import Issues
from bootstrap_datepicker_plus.widgets import DatePickerInput



class IssuesModelForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = Issues
        exclude = ['project', 'creator', 'create_datetime', 'latest_update_datetime']
        
        widgets = {
            "assign": forms.Select(attrs={'class': "selectpicker", 'data-live-search': "true"}),
            "issues_type": forms.Select(attrs={'class': "selectpicker", 'data-live-search': "true"}),
            "module": forms.Select(attrs={'class': "selectpicker", 'data-live-search': "true"}),
            "parent": forms.Select(attrs={'class': "selectpicker", 'data-live-search': "true"}),
            "attention": forms.SelectMultiple(attrs={'class': "selectpicker", 'data-live-search': "true",
                                                     "data-actions-box":"true"}),
            'start_date': DatePickerInput(),  # default date-format %m/%d/%Y will be used
            # specify date-frmat
            'end_date': DatePickerInput(),
        }