from django.http import HttpResponse
from django.shortcuts import redirect
import logging

logger = logging.getLogger(__name__)

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
                '/accounts/logout/',
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
                '/accounts/logout/',
                ],
            'student' : [
                '/',
                '/chem_display/allChemicals/',
                '/chem_display/individualChemicals/',
                '/search/',
                '/scan/',
                '/checkinandout/',
                '/accounts/logout/',
                ],

        }

    def get_user_role(self, user):
            """
            Determine the user's role. This can be based on groups, permissions, or a custom field.
            """
            if user.groups.filter(name='Admin').exists():
                return 'admin'
            elif user.groups.filter(name='Professors').exists():
                return 'professor'
            elif user.groups.filter(name='Students').exists():
                return 'student'
            else:
                return None
    
    def __call__(self, request):
        if request.user.is_superuser:
            logger.info(f"Superuser {request.user.username} accessed {request.path}")
            response = self.get_response(request)
            return response
        
            # Allow access to django-browser-reload paths
        if request.path.startswith('/__reload__/'):
            logger.info(f"Access allowed to django-browser-reload path: {request.path}")
            response = self.get_response(request)
            return response
        
            # Allow access to login and home pages for all users
        if request.path in ['/accounts/login/', '/', '/accounts/signup/', 'accounts/logout/', '/admin/login/', '/admin/' ]:
            logger.info(f"Access allowed to public path: {request.path}")
            response = self.get_response(request)
            return response
    
        
        # Determine the user's role
        user_role = self.get_user_role(request.user)
        logger.info(f"User {request.user.username} with role {user_role} is accessing {request.path}")

        #nick's version
        """ if request.user.has_perm('chemistry_system.can_access_restricted'):
            response = self.get_response(request)
            return response

        if request.path in self.procted_paths:
            return HttpResponse("<h1 style='color:red'>You're not allowed to access this view </h1>", status=403)
             """
        

        # Check if the requested path is protected for the user's role
        if user_role in self.procted_paths:
            # Allow access only if the path is explicitly listed for the user's role
            if request.path not in self.procted_paths[user_role]:
                logger.warning(f"Access denied for user {request.user.username} to {request.path}")
                logger.info(f"Requested path: {request.path}")
                logger.info(f"Allowed paths for role {user_role}: {self.procted_paths[user_role]}")
                return HttpResponse(
                "<h1 style='color:red'>You're not allowed to access this view </h1>",
                status=403,
            )
        else:
            # Block access for users with undefined roles
            logger.warning(f"Access denied for user {request.user.username} to {request.path}")
            logger.info(f"Requested path: {request.path}")
            return HttpResponse(
            "<h1 style='color:red'>You're not allowed to access this view </h1>",
            status=403,
            )

        response = self.get_response(request)
        return response
    
