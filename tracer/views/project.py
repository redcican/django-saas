from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from tracer import models
from tracer.forms.project import ProjectModelForm
from utils.tencent_cos import create_bucket
import time

def project_list(request):
    # GET请求，查看项目
    """
        1. 从数据库中获取所有项目
        1.1 我创建的项目，已星标和未星标
        1.2 我参与的项目，已星标和未星标

        2. 提取已星标的项目
        3. 得到三个列表，星标，创建，参与
    """
    if request.method == 'GET':

        project_dict = {"star_project":[], "my_project":[], "join_project":[]}
        my_project_list = models.Project.objects.filter(creator=request.tracer.user)
        for proj in my_project_list:
            if proj.star:
                project_dict["star_project"].append({'value':proj, 'type':'my_project'})
            else:
                project_dict["my_project"].append(proj)
                
        join_project_list = models.ProjectUser.objects.filter(user=request.tracer.user)
        for item in join_project_list:
            if item.star:
                project_dict["star_project"].append({'value':item.project, 'type':'join_project'})
            else:
                project_dict["join_project"].append(item.project)
        
        form = ProjectModelForm(request)       
        return render(request, 'project_list.html', {'form': form, "project_dict": project_dict})
    
    # POST请求，创建项目, 通过ajax提交
    form = ProjectModelForm(request, data=request.POST)
    if form.is_valid():
        project_name = form.cleaned_data['name'].replace(' ', '').lower()
        # 为项目创建一个Tencent COS Bucket: {phone_number}-{timestamp}-{bucket_prefix}
        # 初始化bucket name 和 region
        mobile_phone = request.tracer.user.mobile_phone.replace('+', '')
        bucket = "{}-{}-{}-1308621155".format(
            project_name, mobile_phone, str(int(time.time()*1000)))
        region = 'ap-shanghai'
        
        create_bucket(bucket, region)
        
        # 把桶和区域信息保存到数据库
        form.instance.bucket = bucket
        form.instance.region = region
        form.instance.creator = request.tracer.user
        form.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'errors': form.errors})


def project_star(request, project_type:str, project_id:int) -> HttpResponse:
    """添加项目的星标

    Args:
        request ([type]): [description]
        project_type (str): 项目的类型，我创建的项目或者我参与的项目
        project_id (int): 要星标的项目ID
    """
    if project_type == 'my_project':
        models.Project.objects.filter(id=project_id, creator=request.tracer.user).update(star=True)
        return redirect('tracer:project_list')
    
    if project_type == 'join_project':
        models.ProjectUser.objects.filter(project_id=project_id, user=request.tracer.user).update(star=True)
        return redirect('tracer:project_list')
    
    return HttpResponse('Request Failed')


def project_unstar(request, project_type:str, project_id:int) -> HttpResponse:
    """去除项目的星标

    Args:
        request ([type]): [description]
        project_type (str): 项目的类型，我创建的项目或者我参与的项目
        project_id (int): 要去除的项目ID
    """
    if project_type == 'my_project':
        models.Project.objects.filter(
            id=project_id, creator=request.tracer.user).update(star=False)
        return redirect('tracer:project_list')

    if project_type == 'join_project':
        models.ProjectUser.objects.filter(
            project_id=project_id, user=request.tracer.user).update(star=False)
        return redirect('tracer:project_list')

    return HttpResponse('Request Failed')
