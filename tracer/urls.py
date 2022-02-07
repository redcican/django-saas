from django.urls import path, re_path
from django.urls.conf import include

from .views import (account, home, project, manage, wiki, file, setting, issues)


app_name = 'tracer'

urlpatterns = [
    path('register/', account.register, name='register'),
    path('login/sms/', account.login_sms, name='login_sms'),
    path('login/', account.login, name='login'),
    path('logout/', account.logout, name='logout'),
    path('image/code/', account.image_code, name='image_code'),
    path('send/sms/', account.send_sms, name='send_sms'),
    path('index/', home.index, name='index'),
    
    # project list
    path('project/list/', project.project_list, name='project_list'),
    re_path('project/star/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_star, name='project_star'),
    re_path('project/unstar/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_unstar, name='project_unstar'),
    
    # project manage
    re_path('manage/(?P<project_id>\d+)/', include([
            re_path('dashboard/$',manage.dashboard, name='dashboard'),
            re_path('statistics/$', manage.statistics, name='statistics'),            
            
            re_path('wiki/$',wiki.wiki, name='wiki'),
            re_path('wiki/add/$',wiki.wiki_add, name='wiki_add'),
            re_path('wiki/catalog/$', wiki.wiki_catalog, name='wiki_catalog'),
            re_path('wiki/delete/(?P<wiki_id>\d+)/$', wiki.wiki_delete, name='wiki_delete'),
            re_path('wiki/edit/(?P<wiki_id>\d+)/$', wiki.wiki_edit, name='wiki_edit'),
            re_path('wiki/upload/$', wiki.wiki_upload, name='wiki_upload'), # upload image to wiki
            
            
            re_path('file/$', file.file, name='file'),
            re_path('file/delete/$', file.file_delete, name='file_delete'),
            re_path('cos/cos_credentials/$',file.cos_credentials, name='cos_credentials'),
            re_path('file/post/$', file.file_post, name='file_post'), # upload file name and size to database
            re_path('file/download/(?P<file_id>\d+)/$', file.file_download, name='file_download'),


            re_path('setting/$',setting.setting, name='setting'),
            re_path('setting/delete/$',setting.setting_delete, name='setting_delete'),
            
            re_path('issues/$',issues.issues, name='issues'),
            re_path('issues/detail/(?P<issue_id>\d+)/$',issues.issues_detail, name='issues_detail'),
            re_path('issues/record/(?P<issue_id>\d+)/$',issues.issues_record, name='issues_record'),

    ])),
]
