from django.http import HttpResponse


class CheckUserRole:
    def __init__(self, get_response):
        self.get_response = get_response
        self.procted_paths = ['/admin-dashboard/']
    
    def __call__(self, request):
        response = self.get_response(request)
        if request.path in self.procted_paths:
            if not request.user.is_superuser:
                return HttpResponse("<h1 style='color:red'>You're not allowed to access this view </h1>", status=403)
        return response