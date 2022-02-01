
from django.http import HttpResponse
from django.shortcuts import redirect, render


def setting(request, project_id):
    return render(request, 'setting.html')

def setting_delete(request, project_id):
    """Delete a project on setting page"""
    if request.method == 'GET':
        return render(request, 'setting_delete.html')
    
    project_name = request.POST.get('project_name')
    
    if not project_name or project_name != request.tracer.project.name:
        return render(request, 'setting_delete.html', {'error':'Wrong project name!'})
    
    # 只有项目的创建者才能删除项目
    if request.tracer.user != request.tracer.project.creator:
        return render(request, 'setting_delete.html', {'error':'You are not the creator of this project!'})
    
    # 删除项目
    # 1. 删除COS Bucket 
    # 1.1 删除 Bucket 中的所有文件
    # 1.2 删除 Bucket 中的文件碎片    
    # 2. 删除项目
    
    return redirect('tracer:project_list')
