import re
from django.utils import timezone
from django.utils.timezone import datetime
from django.shortcuts import render
from django.shortcuts import redirect
from hello.forms import LogChemicalForm
from hello.models import LogChemical
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import CustomLoginForm
from django.contrib.auth.decorators import login_required

class HomeListView(ListView):
    """Renders the home page, with a list of all messages."""
    model = LogChemical

    def get_context_data(self, **kwargs):
        context = super(HomeListView, self).get_context_data(**kwargs)
        return context

def about(request):
    return render(request, "about.html")

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})

def home(request):
    return render(request, "home.html")

def contact(request):
    return render(request, "contact.html")

def log_chemical(request):
    form = LogChemicalForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            chemical = form.save(commit=False)
            chemical.log_date = datetime.now()
            chemical.save()
            return redirect("log")
    else:
        return render(request, "log_message.html", {"form": form})

def delete_chemical(request, id):
    chemical = get_object_or_404(LogChemical, id=id)

    if request.method == "POST":
        chemical.delete()
        return redirect("home")
    
def qr_code_scanner(request):
    return render(request, 'scanner.html')
   

