from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm  # Import the custom form


class SignUpView(CreateView):
    form_class = CustomUserCreationForm  # Use the custom form
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"



@login_required
def approval_pending(request):
    return render(request, "registration/approval-pending.html")