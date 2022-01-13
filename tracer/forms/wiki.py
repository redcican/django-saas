from tracer import models
from django import forms
from tracer.forms.bootstrap import BootstrapForm


class WikiModelForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = models.Wiki
        exclude = ['project', 'depth', ]
        
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        
        # 只显示属于当前project的wiki title
        total_data_list = [("", "---------")]
        data_list = models.Wiki.objects.filter(project=request.tracer.project).values_list('id', 'title')
        total_data_list.extend(data_list)
        self.fields['parent'].choices = total_data_list

    