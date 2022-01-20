
from django import forms
from tracer import models

from tracer.forms.bootstrap import BootstrapForm


class FolderModelForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = models.File
        fields = ['name']
        
    def __init__(self, request,parent_object ,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.parent_object = parent_object
        
    # 禁止文件重名
    def clean_name(self):
        name = self.cleaned_data['name']
        
        # 判断当前目录下是否有同名文件
        queryset = models.File.objects.filter(file_type=2, name=name,
                                              project=self.request.tracer.project)
        if self.parent_object:
            exists = queryset.filter(parent=self.parent_object).exists() # 有父文件件
        else: 
            exists = queryset.filter(parent__isnull=True).exists() # 没有父文件夹
            
        if exists:
            raise forms.ValidationError('Folder name already exists')
        
        return name