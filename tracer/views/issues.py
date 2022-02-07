from django.http import JsonResponse
from django.shortcuts import render
from tracer import models
from tracer.forms.issues import IssuesModelForm
from django.core.paginator import Paginator

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
    issue_object = models.Issues.objects.filter(id=issue_id, project_id=project_id).first()
    form = IssuesModelForm(request, instance=issue_object)

    return render(request, 'issues_detail.html', {'form': form})