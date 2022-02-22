from django.shortcuts import render
from django.http import JsonResponse
from tracer import models
import collections
from django.db.models import Count


def statistics(request, project_id):
    return render(request, 'statistics.html')


def statistics_priority(request, project_id):
    """按优先级生成饼图"""
    # 找到所有的问题，根据优先级分类，每个优先级的数量
    start = request.GET.get('start')
    end = request.GET.get('end')

    data_dict = collections.OrderedDict()
    for key, text in models.Issues.priority_choices:
        data_dict[key] = {'name': text, 'y': 0}

    # 去数据库查询所有分组得到的数据
    result = models.Issues.objects.filter(project_id=project_id, create_datetime__gte=start,
                                          create_datetime__lt=end).values('priority').annotate(ct=Count('id'))

    # 将数据放入字典中
    for item in result:
        data_dict[item['priority']]['y'] = item['ct']
    return JsonResponse({"status": True, "data": list(data_dict.values())})


def statistics_project_user(request, project_id):
    """按项目和用户生成柱状图(每个人被分配的问题数量和类型)"""
    # 1. 所有的项目成员 和 未分配

    start = request.GET.get('start')
    end = request.GET.get('end')

    all_user_dict = collections.OrderedDict()

    all_user_dict[request.tracer.project.creator.id] = {
        'name': request.tracer.project.creator.username,
        'status': {item[0]: 0 for item in models.Issues.status_choices}
    }
    all_user_dict[None] = {
            'name': 'Unassigned',
            'status': {item[0]: 0 for item in models.Issues.status_choices}
        }

    user_list = models.ProjectUser.objects.filter(project_id=project_id)
    for user in user_list:
        all_user_dict[user.user_id] = {
            'name': user.user.username,
            'status': {user[0]: 0 for user in models.Issues.status_choices}
        }

    # 2. 找到所有的问题，根据项目和用户分类，每个用户的问题数量
    issues = models.Issues.objects.filter(project_id=project_id, create_datetime__gte=start,
                                          create_datetime__lt=end)
    for item in issues:
        if not item.assign:
            all_user_dict[None]['status'][item.status] += 1
        else:
            all_user_dict[item.assign_id]['status'][item.status] += 1

    # 3. 获取所有的成员
    categories = [data['name'] for data in all_user_dict.values()]

    data_result_dict = collections.OrderedDict()
    for item in models.Issues.status_choices:
        data_result_dict[item[0]] = {'name': item[1], 'data': []}

    for key, text in models.Issues.status_choices:
        for row in all_user_dict.values():
            count = row['status'][key]
            data_result_dict[key]['data'].append(count)

    context = {
        "status": True,
        "data": {
            'categories': categories,
            'series': list(data_result_dict.values())
        }
    }
    return JsonResponse(context)
