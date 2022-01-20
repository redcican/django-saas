
from django.http import JsonResponse
from django.shortcuts import render
from tracer import models
from tracer.forms.file import FolderModelForm

def file(request, project_id):
    """file list"""
    
    # 判断是否有上级文件夹
    parent_object = None
    folder_id = request.GET.get('folder', "")  # 如果有，则为文件夹，没有则为文件
    if folder_id.isdecimal():
        parent_object = models.File.objects.filter(id=folder_id, file_type=2,
                                                   project=request.tracer.project).first()
    
    if request.method == 'GET':
        
        # 生成table导航条
        breadcrumb_list = []
        parent = parent_object
        while parent:
            breadcrumb_list.insert(0, {'id': parent.id, 'name': parent.name})
            parent = parent.parent
        
        
        # 当前目录下所有的文件和文件夹
        queryset = models.File.objects.filter(project=request.tracer.project)
        
        if parent_object:
            # 进入了某个文件夹
            file_object_list = queryset.filter(parent=parent_object).order_by('-file_type')
            
        else:
            # 没有进入文件夹
            file_object_list = queryset.filter(parent__isnull=True).order_by('-file_type')
        
        form = FolderModelForm(request, parent_object)
        context = {'form': form, 'file_object_list': file_object_list, 'breadcrumb_list': breadcrumb_list}
        return render(request, 'file.html', context)

    
    """POST: add a new folder and edit folder name"""
    
    fid = request.POST.get('fid', "")
    edit_object = None
    if fid.isdecimal():
        # 编辑文件夹名称
        edit_object = models.File.objects.filter(id=fid, file_type=2, project=request.tracer.project).first()
    
    if edit_object:
        form = FolderModelForm(request, parent_object, data=request.POST,instance=edit_object)
    else:
        form = FolderModelForm(request, parent_object, data=request.POST)
    
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.file_type = 2
        form.instance.update_user = request.tracer.user
        form.instance.parent = parent_object
        form.save()
        return JsonResponse({'status': True})
    
    return JsonResponse({'status': False, 'errors': form.errors})