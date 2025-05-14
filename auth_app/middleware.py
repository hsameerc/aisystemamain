# myapp/middleware.py

from django.urls import resolve


class DisableCSRFMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not self._should_apply_csrf(request):
            response.csrf_exempt = True
        return response

    @staticmethod
    def _should_apply_csrf(request):
        login_register_views = ['login', 'register']
        view_name = resolve(request.path_info).view_name
        return view_name.split(':')[-1] not in login_register_views
