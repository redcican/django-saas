from django import forms
from tracer.forms.bootstrap import BootstrapForm
from tracer import models
from tracer.forms.widgets import ColorRadioSelect

class ProjectModelForm(BootstrapForm, forms.ModelForm):
    
    bootstrap_class_exclude = ['color']  # 重写color字段, 可以自定义样式
    
    description = forms.CharField(widget=forms.Textarea, required=False, label='Description')
    class Meta:
        model = models.Project
        fields = ['name', 'color', 'description']
        widgets = {
            'color': ColorRadioSelect(attrs={'class': 'color-radio'}),
        }
        
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        
    def clean_name(self):
        """
        Check project is unique and the user can create project
        """
        name = self.cleaned_data['name']
        creator = self.request.tracer.user
        exists = models.Project.objects.filter(name=name, creator=creator).exists()
        
        if exists:
            raise forms.ValidationError('Project name is already exists')
        
        # 2. 当前用户是否有额度创建项目
        project_number = self.request.tracer.price_policy.project_num
        
        # 3. 当前用户已创建的项目数量
        project_count = models.Project.objects.filter(creator=creator).count()
        
        if project_count >= project_number:
            raise forms.ValidationError('You can not create more projec, please upgrade your plan')
        return name
        

