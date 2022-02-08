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