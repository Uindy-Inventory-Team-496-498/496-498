import re
from hello.forms import EditChemicalForm
from hello.models import QRCodeData, currentlyInStorageTable
from django.views.generic import ListView
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .forms import CustomLoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib import messages

class ChemListView(LoginRequiredMixin,ListView):
    """Renders the home page, with a list of all messages."""
    model = currentlyInStorageTable

    def get_context_data(self, **kwargs):
        context = super(ChemListView, self).get_context_data(**kwargs)
        return context

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

@login_required
def home(request):
    return render(request, "home.html")

@login_required
def qr_code_scan(request):
    return render(request, 'scan.html')

@login_required
def search_qr_code(request):
    chem_id = request.GET.get('chem_id')  # Get chem_id from query parameters
    if not chem_id:
        return JsonResponse({'error': 'No chemical ID provided'}, status=400)

    # Try to get the chemical data from the database
    try:
        chemical = currentlyInStorageTable.objects.get(chemBottleIDNUM=chem_id)  # Assuming chemBottleIDNUM is used as ID
        response_data = {
            'chemName': chemical.chemName,
            'chemLocation': chemical.chemLocation,
            'chemAmountInBottle': chemical.chemAmountInBottle,
            'chemStorageType': chemical.chemStorageType,
        }
        return JsonResponse(response_data)
    except currentlyInStorageTable.DoesNotExist:
        return JsonResponse({'error': 'Chemical not found'}, status=404)


@login_required
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

@login_required
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

@login_required
def add_chemical(request):
    if request.method == 'POST':
        form = EditChemicalForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new chemical data
            messages.success(request, 'Chemical added successfully!')
            return redirect('current_chemicals')  # Redirect to the list view
    else:
        form = EditChemicalForm()

    return render(request, 'add_chemical.html', {'form': form})

@login_required
def delete_chemical(request, id):
    chemical = get_object_or_404(currentlyInStorageTable, id=id)

    if request.method == "POST":
        chemical.delete()
        messages.success(request, 'Chemical deleted successfully!')
        return redirect("current_chemicals")  # Redirect to the list view

    return render(request, 'confirm_delete.html', {'chemical': chemical})