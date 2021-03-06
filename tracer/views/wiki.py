from django.http.response import JsonResponse
from django.shortcuts import redirect, render, reverse
from tracer import models
from django.views.decorators.csrf import csrf_exempt


from tracer.forms.wiki import WikiModelForm
from utils.encrypt import uid
from utils.tencent_cos import upload_buffer_file


def wiki(request, project_id):
    """wiki homepage"""
    
    # show the wiki detail
    wiki_id = request.GET.get('wiki_id')
    
    if not wiki_id or not wiki_id.isdecimal():
        return render(request, 'wiki.html')
    
    if wiki_id:
        wiki_object = models.Wiki.objects.filter(
            id=wiki_id, project_id=project_id).first()
    return render(request, 'wiki.html', {'wiki_object': wiki_object})



def wiki_add(request, project_id):
    """add wiki"""
    if request.method == 'GET':
        form = WikiModelForm(request)
        return render(request, 'wiki_form.html', {'form': form})
    
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
    
    return render(request, 'wiki_form.html', {'form': form})


def wiki_catalog(request, project_id):
    """wiki catalog"""
    data = models.Wiki.objects.filter(
        project_id=project_id).values('id', 'title', 'parent_id').order_by('depth', 'id')
    return JsonResponse({'status': True, 'data': list(data)})


def wiki_delete(request, project_id, wiki_id):
    """Delete a wiki """
    models.Wiki.objects.filter(id=wiki_id, project_id=project_id).delete()
    url = reverse('tracer:wiki', kwargs={'project_id': project_id})
    return redirect(url)

def wiki_edit(request, project_id, wiki_id):
    """Edit a wiki"""
    wiki_object = models.Wiki.objects.filter(id=wiki_id, project_id=project_id).first()
    if not wiki_object:
        url = reverse('tracer:wiki', kwargs={'project_id': project_id})
        return redirect(url)
    
    if request.method == 'GET':
        form = WikiModelForm(request, instance=wiki_object)
        return render(request, 'wiki_form.html', {'form': form})
    
    form = WikiModelForm(request, data=request.POST, instance=wiki_object)
    if form.is_valid():
        
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1
        
        form.save()
        url = reverse('tracer:wiki', kwargs={'project_id': project_id})
        preview_url = "{0}?wiki_id={1}".format(url, wiki_id)
        return redirect(preview_url)
    return render(request, 'wiki_form.html', {form: form})
    
@csrf_exempt
def wiki_upload(request, project_id):
    """upload wiki and issues image to tencent cos"""
    result = {'success': 0, 'message': '', 'url': None}
    
    image_object = request.FILES.get('editormd-image-file')
    
    if not image_object:
        result['message'] = 'no image file'
        return JsonResponse(result)
    
    extension = image_object.name.rsplit('.')[-1]
    key = f"{uid(request.tracer.user.mobile_phone)}.{extension}"
    
    image_url = upload_buffer_file(
        bucket=request.tracer.project.bucket,
        file_object=image_object,
        key=key
    )
    
    result['success'] = 1
    result['url'] = image_url
    
    return JsonResponse(result)
    
    