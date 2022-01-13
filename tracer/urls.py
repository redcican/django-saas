from django.urls import path, re_path
from django.urls.conf import include
from django.conf import settings
from django.conf.urls.static import static

from .views import account
from .views import home
from .views import project
from .views import manage
from .views import wiki

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
            re_path('issues/$',manage.issues, name='issues'),
            re_path('statistics/$', manage.statistics, name='statistics'),
            re_path('file/$',manage.file, name='file'),
            re_path('wiki/$',wiki.wiki, name='wiki'),
            re_path('wiki/add/$',wiki.wiki_add, name='wiki_add'),
            re_path('wiki/catalog/$', wiki.wiki_catalog, name='wiki_catalog'),
            re_path('wiki/delete/(?P<wiki_id>\d+)/$', wiki.wiki_delete, name='wiki_delete'),
            re_path('wiki/edit/(?P<wiki_id>\d+)/$', wiki.wiki_edit, name='wiki_edit'),
            re_path('setting/$',manage.setting, name='setting'),
    ])),
]

    

''''
    # project manage
    re_path('manage/(?P<project_id>\d+)/dashboard/$', project.dashboard, name='project_dashboard'),
    re_path('manage/(?P<project_id>\d+)/issues/$', project.issues, name='project_issues'),
    re_path('manage/(?P<project_id>\d+)/statistics/$',project.statistics, name='project_dstatistics'),
    re_path('manage/(?P<project_id>\d+)/file/$', project.file, name='project_file'),
    re_path('manage/(?P<project_id>\d+)/wiki/$', project.wiki, name='project_wiki'),
    re_path('manage/(?P<project_id>\d+)/setting/$', project.setting, name='project_seting'),
'''