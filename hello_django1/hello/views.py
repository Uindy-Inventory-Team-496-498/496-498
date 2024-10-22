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

class HomeListView(ListView):
    """Renders the home page, with a list of all messages."""
    model = LogChemical

    def get_context_data(self, **kwargs):
        context = super(HomeListView, self).get_context_data(**kwargs)
        return context

def about(request):
    return render(request, "hello/about.html")

def login(request):
    return render(request, "hello/login.html")

def home(request):
    return render(request, "hello/home.html")

def contact(request):
    return render(request, "hello/contact.html")

def log_chemical(request):
    form = LogChemicalForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            chemical = form.save(commit=False)
            chemical.log_date = datetime.now()
            chemical.save()
            return redirect("log")
    else:
        return render(request, "hello/log_message.html", {"form": form})

def delete_chemical(request, id):
    chemical = get_object_or_404(LogChemical, id=id)

    if request.method == "POST":
        chemical.delete()
        return redirect("home")
    
def qr_code_scanner(request):
    return render(request, 'hello/scanner.html')
   

