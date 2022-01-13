from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, reverse
from tracer import models

from tracer.forms.wiki import WikiModelForm


def wiki(request, project_id):
    """wiki homepage"""
    
    # show the wiki detail
    wiki_id = request.GET.get('wiki_id')
    
    if not wiki_id or not wiki_id.isdigit():
        return render(request, 'wiki.html')
    
    if wiki_id:
        wiki_object = models.Wiki.objects.filter(
            id=wiki_id, project_id=project_id).first()
    return render(request, 'wiki.html', {'wiki_object': wiki_object})



def wiki_add(request, project_id):
    """add wiki"""
    if request.method == 'GET':
        form = WikiModelForm(request)
        return render(request, 'wiki_add.html', {'form': form})
    
    form = WikiModelForm(request, data=request.POST)
    if form.is_valid:
        
        # 判断是否有父文章
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1
        
        form.instance.project = request.tracer.project
        form.save()
        url = reverse('tracer:wiki', kwargs={'project_id': project_id})
        return redirect(url)
    
    return render(request, 'wiki_add.html', {'errors': form.errors})


def wiki_catalog(request, project_id):
    """wiki catalog"""
    data = models.Wiki.objects.filter(
        project_id=project_id).values('id', 'title', 'parent_id').order_by('depth', 'id')
    return JsonResponse({'status': True, 'data': list(data)})
