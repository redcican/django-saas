from django import forms
from tracer.forms.bootstrap import BootstrapForm
from tracer.models import Issues


class IssuesModelForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = Issues
        exclude = ['project', 'creator', 'create_datetime', 'latest_update_datetime']