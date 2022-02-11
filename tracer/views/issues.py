import json
from django.http import JsonResponse
from django.shortcuts import render
from tracer import models
from tracer.forms.issues import IssuesModelForm, IssuesReplyModelForm
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import mark_safe


class CheckFilter:
    def __init__(self, request, name, data_list):
        """
        :param request: 请求对象
        :param name: 要创建的checkbox的name
        :param data_list: 在数据库中预定义的tuple类型的数据
        """
        self.data_list = data_list
        self.name = name
        self.request = request

    def __iter__(self):
        for item in self.data_list:
            key, text = str(item[0]), item[1]
            ck = ""
            # 如果当前用户请求的url中包含key，则选中
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:
                ck = "checked"
                value_list.remove(key)
            else:
                value_list.append(key)

            # 将当前的key和value_list放入到request中
            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            query_dict.setlist(self.name, value_list)

            if 'page' in query_dict:
                query_dict.pop('page')

            param_url = query_dict.urlencode()
            if param_url:
                url = "{0}?{1}".format(self.request.path_info, query_dict.urlencode())
            else:
                url = self.request.path_info

            # tpl = '<a class="cell" href="{url}"><input type="checkbox" {ck} /><label>{' \
            #       'text}</label></a>'
            # html = tpl.format(url=url, ck=ck, text=text)
            # yield mark_safe(html)
            yield {"text": text, "url": url, "ck": ck}


def issues(request, project_id):
    if request.method == 'GET':

        allow_filter_list = ['status', 'priority']
        # 筛选条件
        # ?status=1&status=2&priority=2&issues_type=3
        filter_dict = {}
        for name in allow_filter_list:
            value_list = request.GET.getlist(name)  # ['1', '2']
            if not value_list:
                continue
            filter_dict[f"{name}__in"] = value_list
        """
        condition = {
        'status__in': ['1', '2'],
        'priority__in': ['2'],
        }
        """

        form = IssuesModelForm(request)

        issue_object_list = models.Issues.objects.filter(project_id=project_id).filter(
            **filter_dict).order_by('create_datetime')

        paginator = Paginator(issue_object_list, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        choices_filter = []
        for name in allow_filter_list:
            choices_filter.append({
                'name': name.title(),
                'choices': CheckFilter(request, name, models.Issues._meta.get_field(name).choices)})

        return render(request, 'issues.html', {
            'form': form,
            'page_obj': page_obj,
            # 'status_filter': CheckFilter(request, 'status', models.Issues.status_choices),
            # 'priority_filter': CheckFilter(request, 'priority', models.Issues.priority_choices),
            'choices_filter': choices_filter,
        })

    form = IssuesModelForm(request, data=request.POST)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.creator = request.tracer.user
        form.save()

        return JsonResponse({'status': True})

    return JsonResponse({'status': False, 'error': form.errors})


def issues_detail(request, project_id, issue_id):
    """edit the specific issue"""
    issues_object = models.Issues.objects.filter(id=issue_id, project_id=project_id).first()
    form = IssuesModelForm(request, instance=issues_object)

    return render(request, 'issues_detail.html', {'form': form, 'issues_object': issues_object})


@csrf_exempt
def issues_record(request, project_id, issue_id):
    """init issues operation history"""
    if request.method == 'GET':
        reply_list = models.IssuesReply.objects.filter(issues_id=issue_id, issues__project_id=project_id)

        # 将queryset 转换成json格式
        data_list = []
        for row in reply_list:
            data = {
                'id': row.id,
                'reply_type_text': row.get_reply_type_display(),
                'content': row.content,
                'creator': row.creator.username,
                'datetime': row.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                'parent_id': row.reply_id,
            }
            data_list.append(data)

        return JsonResponse({'status': True, 'data': data_list})

    # POST 请求
    form = IssuesReplyModelForm(data=request.POST)
    if form.is_valid():
        form.instance.issues_id = issue_id
        form.instance.reply_type = 2
        form.instance.creator = request.tracer.user
        instance = form.save()
        info = {
            'id': instance.id,
            'reply_type_text': instance.get_reply_type_display(),
            'content': instance.content,
            'creator': instance.creator.username,
            'datetime': instance.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'parent_id': instance.reply_id,
        }
        return JsonResponse({'status': True, 'data': info})

    return JsonResponse({'status': False, 'error': form.errors})


@csrf_exempt
def issues_change(request, project_id, issue_id):
    issues_object = models.Issues.objects.filter(id=issue_id, project_id=project_id).first()
    post_dict = json.loads(request.body.decode('utf-8'))

    name = post_dict.get('name')
    value = post_dict.get('value')
    field_object = models.Issues._meta.get_field(name)

    def create_reply_record(change_record):
        new_object = models.IssuesReply.objects.create(
            reply_type=1,
            issues=issues_object,
            content=change_record,
            creator=request.tracer.user
        )
        data_to_send = {
            'id': new_object.id,
            'reply_type_text': new_object.get_reply_type_display(),
            'content': new_object.content,
            'creator': new_object.creator.username,
            'datetime': new_object.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'parent_id': new_object.reply_id,
        }

        return data_to_send

    # 1. 更新数据库字段
    # 1.1 普通文本  only 'start_date' and 'end_date' can be empty or null
    if name in ['subject', 'desc', 'start_date', 'end_date']:
        if not value:
            if not field_object.null:
                return JsonResponse({'status': False, 'error': f"{field_object.verbose_name} can't be empty"})
            setattr(issues_object, name, None)
            issues_object.save()
            change_record = f"{field_object.verbose_name} was set to empty"
        else:
            setattr(issues_object, name, value)
            issues_object.save()
            change_record = f"{field_object.verbose_name} was set to {value}"

        # 2. 更新issues_reply数据库
        data = create_reply_record(change_record)
        return JsonResponse({'status': True, 'data': data})

    # 1.2 ForeignKey字段， ('assign'要判断是否创建者或参与者)
    if name in ['issues_type', 'module', 'parent', 'assign']:
        if not value:
            # 不允许为空
            if not field_object.null:
                return JsonResponse({'status': False, 'error': f"{field_object.verbose_name} can't be empty"})
            setattr(issues_object, name, None)
            issues_object.save()
            change_record = f"{field_object.verbose_name} was set to empty"
        else:
            if name == 'assign':
                # 是否为项目创建者
                if value == str(request.tracer.project.creator_id):
                    instance = request.tracer.project.creator
                else:
                    # 是否为项目参与者
                    project_user_object = models.ProjectUser.objects.filter(project_id=project_id,
                                                                            user_id=value).first()
                    if project_user_object:
                        instance = project_user_object.user
                    else:
                        instance = None
                if not instance:
                    return JsonResponse({'status': False, 'error': f"{field_object.verbose_name} is not exist"})

                setattr(issues_object, name, instance)
                issues_object.save()
                change_record = f"{field_object.verbose_name} was set to {str(instance)}"

            else:
                instance = field_object.remote_field.model.objects.filter(id=value, project_id=project_id).first()
                if not instance:
                    return JsonResponse({'status': False, 'error': f"{field_object.verbose_name} is not exist"})
                setattr(issues_object, name, instance)
                issues_object.save()
                change_record = f"{field_object.verbose_name} was set to {str(instance)} "

        # 2. 创建操作记录
        data = create_reply_record(change_record)
        return JsonResponse({'status': True, 'data': data})

    # 1.3:choices字段 
    if name in ['status', 'priority', 'mode']:
        selected_text = None
        for key, text in field_object.choices:
            if str(key) == value:
                selected_text = text
        if not selected_text:
            return JsonResponse({'status': False, 'error': f"{field_object.verbose_name} is not exist"})

        setattr(issues_object, name, value)
        issues_object.save()
        change_record = f"{field_object.verbose_name} was set to {selected_text}"
        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})

    # 1.4 ManyToManyField字段
    if name == "attention":
        # {"name": "attention", "value": "[1,2,3]"}
        if not isinstance(value, list):
            return JsonResponse({'status': False, 'error': f"{field_object.verbose_name} is not exist"})

        if not value:
            issues_object.attention.set(value)
            issues_object.save()
            change_record = f"{field_object.verbose_name} was set to empty"

        else:
            # value: [1,2,3] -> 判断id是否为项目成员 (参与者或创建者)
            # 获取当前项目的所有成员
            user_dict = {str(request.tracer.project.creator_id): request.tracer.project.creator.username}
            project_user_list = models.ProjectUser.objects.filter(project_id=project_id)
            for item in project_user_list:
                user_dict[str(item.user_id)] = item.user.username

            username_list = []
            for user_id in value:
                username = user_dict.get(str(user_id))
                if not username:
                    return JsonResponse({'status': False, 'error': 'User is not exist, please check again'})
                username_list.append(username)

            issues_object.attention.set(value)
            issues_object.save()
            change_record = f"{field_object.verbose_name} was set to {','.join(username_list)}"

        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})

    return JsonResponse({'status': False, 'error': 'Invalid field name'})
