# myapp/middleware.py

class AdminSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.conf import settings
        if request.path.startswith('/kisan-admin/'):
            settings.SESSION_COOKIE_NAME = 'admin_sessionid'
        else:
            settings.SESSION_COOKIE_NAME = 'user_sessionid'
        return self.get_response(request)