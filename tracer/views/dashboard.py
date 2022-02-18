from django.shortcuts import render
from tracer import models
from django.db.models import Count


def dashboard(request, project_id):
    # issues status
    status_dict = {}
    for key, text in models.Issues.status_choices:
        status_dict[key] = {'text': text, 'count': 0}

    issues_data = models.Issues.objects.filter(project_id=project_id).values('status').annotate(ct=Count('id'))
    for item in issues_data:
        status_dict[item['status']]['count'] = item['ct']

    # project user
    user_list = models.ProjectUser.objects.filter(project_id=project_id).values('user_id', 'user__username')

    # top 10 issues assignee 并且指派者不为空
    top_ten = models.Issues.objects.filter(project_id=project_id, assign__isnull=False).order_by('-id')[:10]
    context = {
        'status_dict': status_dict,
        'user_list': user_list,
        'top_ten': top_ten,
    }
    return render(request, 'dashboard.html', context)
