
from django import forms
from tracer import models

from tracer.forms.bootstrap import BootstrapForm
from utils.tencent_cos import check_file_exist
from qcloud_cos.cos_exception import CosServiceError



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
    
    
class FileModelForm(forms.ModelForm):
    
    etag = forms.CharField(label='ETag') # 额外创建etag字段，用来比较上传的文件和服务器上的文件是否一致
    
    class Meta:
        model = models.File
        exclude = ['file_type', 'project', 'update_user', 'update_datetime']
        
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        
    def clean_file_path(self):
        return f"https://{self.cleaned_data['file_path']}"
    
    def clean(self):
        etag = self.cleaned_data.get('etag') # 向COS校验文件是否合法
        key = self.cleaned_data.get('key') # 向COS校验文件是否合法
        file_size = self.cleaned_data.get('file_size') # 向COS校验文件是否合法
        
        if not etag and not key:
            return self.cleaned_data
        
        # 向COS校验文件是否合法
        try:
            response = check_file_exist(self.request.tracer.project.bucket, key)
        except:
            self.add_error("key", "File does not exist")
            return self.cleaned_data
        
        if response.get('ETag') != etag:
            self.add_error('etag', 'File is not valid')
        
        object_size = response.get('Content-Length')
        if int(object_size) != int(file_size):
            self.add_error('size', 'File is not valid')
            
        return self.cleaned_data