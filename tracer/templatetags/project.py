from django.template import Library
from tracer import models

register = Library()

@register.inclusion_tag('inclusion/all_project_list.html')
def all_project_list(request):
    # 1. 我创建的所有项目
    my_project_list = models.Project.objects.filter(creator=request.tracer.user)
    # 2. 我参与的所有项目
    join_project_list = models.ProjectUser.objects.filter(user=request.tracer.user)
    return {'my_project': my_project_list, 'join_project': join_project_list}
