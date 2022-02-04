from django.http import JsonResponse
from django.shortcuts import render
from tracer import models
from tracer.forms.issues import IssuesModelForm

def issues(request, project_id):
    
    if request.method == 'GET':
        form = IssuesModelForm(request)
        
        issue_object_list = models.Issues.objects.filter(project_id=project_id)
        
        return render(request, 'issues.html', {'form': form, 'issue_object_list': issue_object_list})
    
    form = IssuesModelForm(request, data=request.POST)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.creator = request.tracer.user
        form.save()
        
        return JsonResponse({'status': True})
    
    return JsonResponse({'status': False, 'error': form.errors})