
from hashlib import new
from django.shortcuts import redirect, render
from tracer import models
from tracer.forms.account import ChangePasswordForm

from utils.tencent_cos import delete_bucket
from django.contrib.auth.forms import PasswordChangeForm
from utils.encrypt import md5

def setting(request, project_id):
    return render(request, 'setting.html')

def setting_delete(request, project_id):
    """Delete a project on setting page"""

    original_project_name = request.tracer.project.name
    if request.method == 'GET':

        return render(request, 'setting_delete.html', {'original_project_name': original_project_name})
    
    project_name = request.POST.get('project_name')
    
    if not project_name or project_name != request.tracer.project.name:
        return render(request, 'setting_delete.html', {'error': 'Wrong project name!',
                                                       'original_project_name': original_project_name})
    
    # 只有项目的创建者才能删除项目
    if request.tracer.user != request.tracer.project.creator:
        return render(request, 'setting_delete.html', {'error': 'You are not the creator of this project!',
                                                       'original_project_name': original_project_name})
    
    # 删除项目
    # 1. 删除COS Bucket 
    # 1.1 删除 Bucket 中的所有文件
    # 1.2 删除 Bucket 中的文件碎片    
    # 2. 删除项目
    delete_bucket(request.tracer.project.bucket, request.tracer.project.region)
    models.Project.objects.filter(id=request.tracer.project.id).delete()
    
    return redirect('tracer:project_list')


def change_password(request, project_id):
    """Change password"""
    if request.method == 'GET':
        form = ChangePasswordForm(request)
        return render(request, 'change_password.html', {'form': form})
    
    else:
        form = ChangePasswordForm(request, data=request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            
            request.tracer.user.password = md5(new_password)
            request.tracer.user.save()
            return redirect('tracer:login')
        else:
            return render(request, 'change_password.html', {'form': form})