from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

class ApprovalRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_approved:
            messages.error(request, "Your account is not approved yet.")
            logout(request)
            return redirect('login')
        return self.get_response(request)