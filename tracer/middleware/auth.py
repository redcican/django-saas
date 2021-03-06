from django.utils.deprecation import MiddlewareMixin
from tracer import models
from django.conf import settings
from django.shortcuts import redirect
import datetime


class Tracer(object):
    def __init__(self):
        self.user = None
        self.price_policy = None
        self.project = None


class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        """
        If user has login, assign a value into 'request'
        """

        request.tracer = Tracer()

        user_id = request.session.get('user_id', 0)
        user_object = models.UserInfo.objects.filter(id=user_id).first()

        request.tracer.user = user_object

        """
        white list:
        1. 检查当前用户访问的URL
        2. 检查URL是否在白名单中, 如果在白名单中, 则放行, 否则返回登陆页面
        """
        if request.path_info in settings.WHITE_REGEX_URL_LIST:
            return

        if not request.tracer.user:
            return redirect('tracer:login')

        # 获取当前用户的额度
        # 获取当前用户的ID最大值 （最近交易记录）status=2 表示为付费用户
        _object = models.Transaction.objects.filter(user=user_object, status=2).order_by('-id').first()

        # 判断当前用户的订阅是否过期
        current_datetime = datetime.datetime.now()
        # 如果为免费用户，并且当前时间在订阅时间之前
        if _object.end_datetime and _object.end_datetime < current_datetime:
            _object = models.Transaction.objects.filter(user=user_object, status=2,
                                                        price_policy__category=1).first()

        request.tracer.price_policy = _object.price_policy

    def process_view(self, request, view, args, kwargs):

        # 判断URL是否以manage开头，如果是，则判断项目ID是否我创建 or 参与
        if not request.path_info.startswith('/manage/'):
            return

        # project_id 是我创建 or 我参与的项目的ID
        project_id = kwargs.get('project_id')

        # 判断是否是我创建的项目
        project_object = models.Project.objects.filter(creator=request.tracer.user, id=project_id).first()

        if project_object:
            request.tracer.project = project_object
            return

            # 判断是否是我参与的项目
        project_user_object = models.ProjectUser.objects.filter(user=request.tracer.user, project_id=project_id).first()

        if project_user_object:
            request.tracer.project = project_user_object.project
            return

        return redirect('tracer:project_list')
