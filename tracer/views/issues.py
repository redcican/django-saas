import json
from django.http import JsonResponse
from django.shortcuts import render
from tracer import models
from tracer.forms.issues import IssuesModelForm, IssuesReplyModelForm
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

def issues(request, project_id):
    
    if request.method == 'GET':
        form = IssuesModelForm(request)
        
        issue_object_list = models.Issues.objects.filter(project_id=project_id).order_by('create_datetime')
        
        paginator = Paginator(issue_object_list, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'issues.html', {'form': form, 'page_obj': page_obj})
    
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
                'parent_id':row.reply_id,
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

    # 1. 更新数据库字段
    # 1.1 普通文本  only 'start_date' and 'end_date' can be empty or null
    if name in ['subject', 'desc','start_date','end_date']:
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
        instance = models.IssuesReply.objects.create(
            reply_type=1,
            issues = issues_object,
            content = change_record,
            creator = request.tracer.user
        )
        data = {
            'id': instance.id,
            'reply_type_text': instance.get_reply_type_display(),
            'content': instance.content,
            'creator': instance.creator.username,
            'datetime': instance.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'parent_id': instance.reply_id,
        }
        return JsonResponse({'status':True, 'data': data})
    # 1.2 ForeignKey字段， 1.3:choices字段 1.4 ManyToManyField字段
    
    # 2. 创建操作记录
    return JsonResponse({'status': True})