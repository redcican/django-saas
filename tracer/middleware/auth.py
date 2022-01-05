from django.utils.deprecation import MiddlewareMixin
from tracer import models

class AuthMiddleware(MiddlewareMixin):
    
    def process_request(self, request):
        """
        If user has login, assign a value into 'request'
        """
        user_id = request.session.get('user_id', 0)
        user_object = models.UserInfo.objects.filter(id=user_id).first()
        if user_object:
            request.tracer = user_object