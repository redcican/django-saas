from django.http.response import JsonResponse
from django.shortcuts import render
from tracer.forms.project import ProjectModelForm

def project_list(request):

    if request.method == 'GET':
        form = ProjectModelForm(request)
        
        return render(request, 'project_list.html', {'form': form})
    
    form = ProjectModelForm(request, data=request.POST)
    if form.is_valid():
        form.instance.creator = request.tracer.user
        form.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'errors': form.errors})