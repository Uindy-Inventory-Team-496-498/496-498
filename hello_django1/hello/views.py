import re
from django.utils import timezone
from django.utils.timezone import datetime
from hello.forms import LogChemicalForm
from hello.forms import EditChemicalForm
from hello.models import LogChemical
from hello.models import LogChemical, QRCodeData, currentlyInStorageTable
from django.views.generic import ListView
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .forms import CustomLoginForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages

class ChemListView(ListView):
    """Renders the home page, with a list of all messages."""
    model = currentlyInStorageTable

    def get_context_data(self, **kwargs):
        context = super(ChemListView, self).get_context_data(**kwargs)
        return context
		
def edit_chemical(request, id):
    chemical = get_object_or_404(currentlyInStorageTable, pk=id)
    if request.method == 'POST':
        # Use the EditChemicalForm to handle form submission
        form = EditChemicalForm(request.POST, instance=chemical)
        if form.is_valid():
            form.save()  # Save the updated chemical data
            messages.success(request, 'Chemical updated successfully!')  # Add a success message
            return redirect('current_chemicals')  # Redirect back to the list view
    else:
        # Create the form with the existing chemical data pre-filled
        form = EditChemicalForm(instance=chemical)
    return render(request, 'edit_chemical.html', {'form': form, 'chemical': chemical})

class HomeListView(ListView):
    """Renders the home page, with a list of all messages."""
    model = LogChemical

    def get_context_data(self, **kwargs):
        context = super(HomeListView, self).get_context_data(**kwargs)
        return context

def about(request):
    return render(request, "about.html")

def current_chemicals(request):
    return render(request, "currchemicals.html")

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

def qr_code_scan(request):
    return render(request, 'scan.html')

def search_qr_code(request, qr_code):
    record = get_object_or_404(QRCodeData, qr_code=qr_code)  # Query using the QR code data
    response_data = {
        'id': record.id,
        'name': record.name,
        'description': record.description,
    }
    return JsonResponse(response_data)


def search_by_qr_code(request):
    chem_id = request.GET.get('chem_id')  # assuming the QR code scanner sends the ID as 'chem_id'
    try:
        chemical = currentlyInStorageTable.objects.get(chemBottleIDNUM=chem_id)
        data = {
            "chemName": chemical.chemName,
            "chemLocation": chemical.chemLocation,
            "chemAmountInBottle": chemical.chemAmountInBottle,
            "chemStorageType": chemical.chemStorageType,
        }
        return JsonResponse(data, status=200)
    except currentlyInStorageTable.DoesNotExist:
        return JsonResponse({"error": "Chemical not found."}, status=404)
    else:
        return JsonResponse({"error": "Invalid search input."}, status=400) 
    
def searching(request):
	#filter() returns row matching search value, need to pull input from user
	#, right now just using bottleIDNUM for ease of integrating barcode scanner
	searchData = currentlyInStorageTable.objects.filter(chemBottleIDNUM_exacts=1).values()
	template = loader.get_template('template.html')
	context = {
		'currentlyInStorageTableSearch': searchData,
	}
	return HttpResponse(template.render(context, request))

# Basic Search Implementation
def basic_search(request):
    query = request.GET.get('query', '')  # Get the search term from the request
    results = currentlyInStorageTable.objects.filter(
        chemBottleIDNUM__icontains=query
    ) | currentlyInStorageTable.objects.filter(
        chemName__icontains=query
    )  # Search by ID or name using icontains for partial matches
    
    return render(request, 'search_results.html', {'results': results, 'query': query})

def search_page(request):
    query = request.GET.get('query', '').strip()
    results = []
    message = None

    if query:
        results = currentlyInStorageTable.objects.filter(
            chemName__icontains=query
        ) | currentlyInStorageTable.objects.filter(
            chemBottleIDNUM__icontains=query
        )
        if not results:
            message = "No results found."
    elif request.GET:
        message = "Please enter a search term."

    return render(request, 'search.html', {
        'results': results,
        'query': query,
        'message': message
    })