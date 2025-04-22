from django.http import HttpResponse
from django.shortcuts import redirect

class CheckUserRole:
    def __init__(self, get_response):
        self.get_response = get_response
        self.procted_paths = {
            'admin' : [
                '/',
                '/admin-dashboard/',
                '/chem_display/allChemicals/',
                '/chem_display/individualChemicals/',
                '/search/',
                '/scan/',
                '/checkinandout/',
                '/print/',
                '/log/',
                ],
            'professor' : [
                '/',
                '/chem_display/allChemicals/',
                '/chem_display/individualChemicals/',
                '/search/',
                '/scan/',
                '/checkinandout/',
                '/print/',
                '/log/',
                ],
            'student' : [
                '/',
                '/chem_display/allChemicals/',
                '/chem_display/individualChemicals/',
                '/search/',
                '/scan/',
                '/checkinandout/',
                ],

        }

    def get_user_role(self, user):
            """
            Determine the user's role. This can be based on groups, permissions, or a custom field.
            """
            if user.groups.filter(name='Admin').exists():
                return 'admin'
            elif user.groups.filter(name='Professor').exists():
                return 'professor'
            elif user.groups.filter(name='Student').exists():
                return 'student'
            else:
                return None
    
    def __call__(self, request):
        if request.user.is_superuser:
            response = self.get_response(request)
            return response
    
        
        # Determine the user's role
        user_role = self.get_user_role(request.user)

        #nick's version
        """ if request.user.has_perm('chemistry_system.can_access_restricted'):
            response = self.get_response(request)
            return response

        if request.path in self.procted_paths:
            return HttpResponse("<h1 style='color:red'>You're not allowed to access this view </h1>", status=403)
             """
        

        # Check if the requested path is protected for the user's role
        if user_role in self.procted_paths:
            if request.path not in self.procted_paths[user_role]:
                return HttpResponse(
                    "<h1 style='color:red'>You're not allowed to access this view </h1>",
                    status=403,
                )

        response = self.get_response(request)
        return response
    
