import collections
import datetime
import time

from django.shortcuts import render
from tracer import models
from django.db.models import Count
from django.http import JsonResponse


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


def issues_chart(request, project_id):
    # 最近30天，每天创建的issue数量 & 根据每天的数量分组
    today = datetime.date.today()
    result = models.Issues.objects.filter(project_id=project_id, create_datetime__gte=today - datetime.timedelta(days=30)).extra(
        select={'ctime': "to_char(tracer_issues.create_datetime,'YYYY-MM-DD')"}).values('ctime').annotate(ct=Count('id'))

    # result: <QuerySet [{'ctime': '2022-02-09', 'ct': 1}, {'ctime': '2022-02-08', 'ct': 1}]>
    date_dict = collections.OrderedDict()
    for i in range(30):
        date = today - datetime.timedelta(days=i)
        date_dict[date.strftime('%Y-%m-%d')] = [time.mktime(date.timetuple())*1000, 0]

    for item in result:
        date_dict[item['ctime']][1] = item['ct']
    return JsonResponse({'status': 'true', 'data': list(date_dict.values())})