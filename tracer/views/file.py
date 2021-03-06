import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from tracer import models
from tracer.forms.file import FolderModelForm, FileModelForm
from utils.encrypt import bytes_readable
from utils.tencent_cos import create_crendentials, delete_file, delete_file_list
import requests
from django.utils.encoding import escape_uri_path


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
        context = {
            'form': form,
            'file_object_list': file_object_list,
            'breadcrumb_list': breadcrumb_list,
            'folder_object': parent_object
        }

        return render(request, 'file.html', context)

    """POST: add a new folder and edit folder name"""

    fid = request.POST.get('fid', "")
    edit_object = None
    if fid.isdecimal():
        # 编辑文件夹名称
        edit_object = models.File.objects.filter(id=fid, file_type=2, project=request.tracer.project).first()

    if edit_object:
        form = FolderModelForm(request, parent_object, data=request.POST, instance=edit_object)
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


def file_delete(request, project_id):
    """delete a file or a folder"""

    fid = request.GET.get('fid', "")
    current_project = request.tracer.project

    # 删除数据库中的文件或文件夹 (级联删除)
    delete_object = models.File.objects.filter(id=fid, project=current_project).first()

    if delete_object.file_type == 1:
        # 删除文件 (数据库文件删除， cos文件删除， 当前项目已使用的空间容量要重置)
        current_project.use_space -= delete_object.file_size
        current_project.save()

        # delete cos file
        delete_file(current_project.bucket, delete_object.key)

        # delete database file
        delete_object.delete()

        return JsonResponse({'status': True})

    # else:
    #     # 删除文件夹 (打到该文件夹下所有的文件， 删除， cos文件删除， 当前项目已使用的空间容量要重置)
    #     pass

    else:
        total_size = 0
        key_list = []  # 要删除的cos文件的key列表

        folder_list = [delete_object, ]
        for folder in folder_list:
            child_list = models.File.objects.filter(parent=folder, project=current_project).order_by('-file_type')

            for child in child_list:
                if child.file_type == 2:
                    folder_list.append(child)
                else:
                    # 文件大小汇总
                    total_size += child.file_size

                    # 删除cos文件
                    key_list.append({'key': child.key})

        # cos 批量删除文件
        if key_list:
            delete_file_list(current_project.bucket, key_list)

        # 更新数据库
        if total_size:
            current_project.use_space -= total_size
            current_project.save()

        # 删除数据库文件
        delete_object.delete()
        return JsonResponse({'status': True})


@csrf_exempt
def cos_credentials(request, project_id):
    """获取tencent cos的临时凭证"""
    # 做容量限制: 单个文件 和 项目总容量
    per_file_limit = request.tracer.price_policy.per_file_size  # in MB
    project_space = request.tracer.price_policy.project_space

    # used project space
    used_project_space = request.tracer.project.use_space

    per_file_limit_byte = per_file_limit * 1024 * 1024  # in Byte
    total_file_limit_byte = project_space * 1024 * 1024 * 1024  # in Byte

    file_list = json.loads(request.body.decode('utf-8'))

    total_size = 0

    for item in file_list:
        if item['size'] > per_file_limit_byte:
            msg = f"Single file size cannot exceed {per_file_limit} MB, File name: {item['name']}, Please upgrade your plan"
            return JsonResponse({'status': False, 'error': msg})

        total_size += item['size']

    # 判断总容量是否超过限制
    if used_project_space + total_size > total_file_limit_byte:
        return JsonResponse({'status': False, 'error': 'Project used space exceeded, Please upgrade your plan'})

    response = create_crendentials(request.tracer.project.bucket)
    return JsonResponse({'status': True, 'data': response})


@csrf_exempt  # ajax post cors request
def file_post(request, project_id):
    """将已经上传的文件信息写入数据库
    
    name: fileName,
    key: key,
    file_size: fileSize,
    parent: CURRENT_FOLDER_ID,
    etag: data.ETag,
    file_path: data.Location,
    """

    form = FileModelForm(request, data=request.POST)

    if form.is_valid():
        data_dict = form.cleaned_data
        data_dict.pop('etag')
        data_dict.update(
            {'project': request.tracer.project, 'file_type': 1, 'update_user': request.tracer.user})

        instance = models.File.objects.create(**data_dict)
        # file_size_readable = bytes_readable(instance.file_size)

        # 更新项目已使用空间
        request.tracer.project.use_space += instance.file_size
        request.tracer.project.save()

        result = {
            'id': instance.id,
            'name': instance.name,
            'file_size': instance.file_size,
            'username': instance.update_user.username,
            'datetime': instance.update_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'download_url': reverse('tracer:file_download', kwargs={'project_id': project_id, 'file_id': instance.id}),
            # 'file_type': instance.get_file_type_display(),
        }
        return JsonResponse({'status': True, 'data': result})

    return JsonResponse({'status': False, 'errors': form.errors})


def file_download(request, project_id, file_id):
    # 找到要下载的文件
    file_object = models.File.objects.filter(id=file_id, project=request.tracer.project).first()

    res = requests.get(file_object.file_path)

    # 文件分块下载
    data = res.iter_content()

    # 设置content-type=application/octet-stream 用于提示下载框
    response = HttpResponse(data, content_type='application/octet-stream')

    # 设置响应头，用于中文文件名转义
    response['Content-Disposition'] = f'attachment; filename={escape_uri_path(file_object.name)}'

    return response
