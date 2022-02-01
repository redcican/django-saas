from django.template import Library
from tracer import models
from django.shortcuts import reverse

register = Library()

@register.inclusion_tag('inclusion/all_project_list.html')
def all_project_list(request):
    # 1. 我创建的所有项目
    my_project_list = models.Project.objects.filter(creator=request.tracer.user)
    # 2. 我参与的所有项目
    join_project_list = models.ProjectUser.objects.filter(user=request.tracer.user)
    return {'my_project': my_project_list, 'join_project': join_project_list, 'request': request}


@register.inclusion_tag('inclusion/manage_menu_list.html')
def manage_menu_list(request):
    data_list = [
        {'title': 'Dashboard', 'url': reverse('tracer:dashboard', kwargs={
                                              'project_id': request.tracer.project.id})},
        {'title': 'Issues', 'url': reverse('tracer:issues', kwargs={'project_id': request.tracer.project.id})},
        {'title': 'Statistics', 'url': reverse('tracer:statistics', kwargs={'project_id': request.tracer.project.id})},
        {'title': 'Wiki', 'url': reverse('tracer:wiki', kwargs={'project_id': request.tracer.project.id})},
        {'title': 'File', 'url': reverse('tracer:file', kwargs={'project_id': request.tracer.project.id})},
        {'title': 'Settings', 'url': reverse('tracer:setting', kwargs={'project_id': request.tracer.project.id})},
    ]
    
    for item in data_list:
        if request.path_info.startswith(item['url']):
            item['class'] = 'active'
    
    return {'data_list': data_list}