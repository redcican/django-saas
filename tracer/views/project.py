from django.http.response import JsonResponse
from django.shortcuts import render
from tracer import models
from tracer.forms.project import ProjectModelForm

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
                project_dict["star_project"].append(proj)
            else:
                project_dict["my_project"].append(proj)
                
        join_project_list = models.ProjectUser.objects.filter(user=request.tracer.user)
        for item in join_project_list:
            if item.star:
                project_dict["star_project"].append(item.project)
            else:
                project_dict["join_project"].append(item.project)
        
        form = ProjectModelForm(request)       
        return render(request, 'project_list.html', {'form': form, "project_dict": project_dict})
    # POST请求，创建项目, 通过ajax提交
    form = ProjectModelForm(request, data=request.POST)
    if form.is_valid():
        form.instance.creator = request.tracer.user
        form.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'errors': form.errors})