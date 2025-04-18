from django.http import HttpResponse
from django.shortcuts import redirect

class CheckUserRole:
    def __init__(self, get_response):
        self.get_response = get_response
        self.procted_paths = [
                            '/admin-dashboard/',
                            '/chem_display/allChemicals/',
                            '/chem_display/individualChemicals/',
                            '/search/',
                            '/scan/',
                            '/checkinandout/',
                            '/print/',
                            '/log/',
                              ]
    
    def __call__(self, request):
        if request.user.is_superuser:
            response = self.get_response(request)
            return response
        
        if request.user.has_perm('chemistry_system.can_access_restricted'):
            response = self.get_response(request)
            return response

        if request.path in self.procted_paths:
            return HttpResponse("<h1 style='color:red'>You're not allowed to access this view </h1>", status=403)
            
        response = self.get_response(request)
        return response