import re
from django.utils.timezone import datetime
from django.shortcuts import render
from django.shortcuts import redirect
from hello.forms import LogMessageForm
from hello.models import LogMessage
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

class HomeListView(ListView):
    """Renders the home page, with a list of all messages."""
    model = LogMessage

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

def log_message(request):
    form = LogMessageForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            message = form.save(commit=False)
            message.log_date = datetime.now()
            message.save()
            return redirect("log")
    else:
        return render(request, "hello/log_message.html", {"form": form})
    
def delete_message(request, id):
    message = get_object_or_404(LogMessage, id=id)

    if request.method == "POST":
        message.delete()
        return redirect("home")
   

