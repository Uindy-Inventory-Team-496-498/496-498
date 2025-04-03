from django.shortcuts import redirect

class ApprovalRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_approved:
            return redirect('approval_pending')  # Redirect to a "pending approval" page
        return self.get_response(request)