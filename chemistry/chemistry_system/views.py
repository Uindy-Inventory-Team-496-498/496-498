import csv
from datetime import datetime
from django.views.generic import ListView
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils.timezone import now
from django.core.paginator import Paginator
from chemistry_system.models import allChemicalsTable, currentlyInStorageTable, Log, get_model_by_name
from .forms import CustomLoginForm, get_dynamic_form, CSVUploadForm, CurrChemicalForm
from .utils import update_total_amounts, logCall, generate_qr_pdf, export_chemicals_csv, import_chemicals_csv, update_checkout_status

class ChemListView(LoginRequiredMixin, ListView):
    """Renders the home page, with a list of all messages."""
    model = currentlyInStorageTable

    def get_context_data(self, **kwargs):
        context = super(ChemListView, self).get_context_data(**kwargs)
        return context

@login_required
def currchemicals(request):
    chemical_list_db = currentlyInStorageTable.objects.select_related('chemAssociated').all()
    chemical_types = allChemicalsTable.objects.values_list('chemMaterial', flat=True).distinct()
    chemical_locations = currentlyInStorageTable.objects.values_list('chemAssociated__chemLocationRoom', flat=True).distinct()

    return render(request, 'currchemicals.html', {
        'chemical_list_db': chemical_list_db,
        'chemical_types': chemical_types,
        'chemical_locations': chemical_locations
    })

@login_required
def allchemicals(request):
    update_total_amounts()  # Update total amounts before rendering
    chemical_list_db = allChemicalsTable.objects.all()
    chemical_types = allChemicalsTable.objects.values_list('chemMaterial', flat=True).distinct()
    chemical_locations = allChemicalsTable.objects.values_list('chemLocationRoom', flat=True).distinct()

    return render(request, 'all_chemicals.html', {
        'chemical_list_db': chemical_list_db,
        'chemical_types': chemical_types,
        'chemical_locations': chemical_locations
    })

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
    return render(request, 'scan.html') # Only if you need to disable CSRF for testing

@login_required
def search_page(request):
    query = request.GET.get('query', '').strip()
    results = currentlyInStorageTable.objects.none()
    message = None

    if query:
        if query.isdigit():
            # If user typed only digits, match bottle ID EXACTLY (no name match).
            results = currentlyInStorageTable.objects.filter(
                chemBottleIDNUM__iexact=query
            )
        else:
            # If query is non-numeric, match names by partial or startswith, etc.
            results = currentlyInStorageTable.objects.filter(
                chemAssociated__chemName__icontains=query
            )

        if results.exists():
            count = results.count()
            message = f"{count} result{'s' if count > 1 else ''} found"
        else:
            message = f"No results found for '{query}'."
    elif request.GET:
        message = "Please enter a search term."

    # Paginate
    paginator = Paginator(results, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'search.html', {
        'results': page_obj,
        'query': query,
        'message': message,
    })

@login_required
def live_search_api(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse([], safe=False)

    # If the user typed only digits, do exact match on ID; otherwise do 'starts with' on chemAssociated__chemName.
    if query.isdigit():
        # We want ID == query OR name starts with query (in case you still want name matches).
        matches = currentlyInStorageTable.objects.filter(
            Q(chemAssociated__chemName__istartswith=query) | Q(chemBottleIDNUM__iexact=query)
        )
    else:
        # If it's non-numeric, match only names that start with the query.
        matches = currentlyInStorageTable.objects.filter(
            Q(chemAssociated__chemName__istartswith=query)
        )
    
    data = [
        {'chemName': m.chemAssociated.chemName, 'chemBottleIDNUM': m.chemBottleIDNUM}
        for m in matches
    ]
    return JsonResponse(data, safe=False)

@login_required
def add_chemical(request, model_name):
    if model_name.lower() == 'currentlyinstoragetable':
        form_class = CurrChemicalForm
    else:
        form_class = get_dynamic_form(model_name)

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            chem_bottle_id = form.cleaned_data.get('chemBottleIDNUM')
            form.save()
            logCall(request.user.username, f"Added chemical to {model_name} with ID: {chem_bottle_id}")
            messages.success(request, 'Chemical added successfully!')
            return redirect('currchemicals')
    else:
        form = form_class()

    return render(request, 'add_chemical.html', {'form': form, 'model_name': model_name})

@login_required
def scanner_add(request):
    return render(request, 'scanner_add.html')

@login_required
def edit_chemical(request, model_name, pk):
    model_class = get_model_by_name(model_name)
    model = model_class[0]
    if not model:
        return render(request, '404.html', status=404)
    
    chemical = get_object_or_404(model, pk=pk)
    DynamicChemicalForm = get_dynamic_form(model_name)
    
    if request.method == 'POST':
        form = DynamicChemicalForm(request.POST, instance=chemical)
        if form.is_valid():
            logCall(request.user.username, f"Updated chemical with ID {pk}")
            form.save()
            messages.success(request, 'Chemical updated successfully!')
            return redirect('currchemicals')
    else:
        form = DynamicChemicalForm(instance=chemical)
    
    return render(request, 'edit_chemical.html', {'form': form, 'chemical': chemical, 'model_name': model_name})

@login_required
def delete_chemical(request, model_name, pk):
    model_class = get_model_by_name(model_name)
    model = model_class[0]
    if not model:
        return render(request, '404.html', status=404)
    
    chemical = get_object_or_404(model, pk=pk)
    
    if request.method == 'POST':
        chemical.delete()
        logCall(request.user.username, f"Deleted chemical with ID {pk}")
        messages.success(request, 'Chemical deleted successfully!')
        return redirect('currchemicals')
    
    return render(request, 'confirm_delete.html', {'chemical': chemical})

@login_required
def delete_all_chemicals(request):
    if request.method == 'POST':
        model_name = request.POST.get('model_name', 'currentlyinstoragetable')
        model_class, _ = get_model_by_name(model_name)
        
        if model_class:
            row_count = model_class.objects.count()
            model_class.objects.all().delete()
            logCall(request.user.username, f"Deleted {row_count} rows from {model_name}")
            messages.success(request, 'All chemicals have been deleted successfully!')
        else:
            messages.error(request, 'Invalid model name.')

        return redirect('currchemicals' if model_name == 'currentlyinstoragetable' else 'allchemicals')
    return render(request, 'confirm_delete_all.html')

@login_required
def list_chemicals(request, model_name):
    model_class = get_model_by_name(model_name)
    model = model_class[0]
    if not model:
        return render(request, '404.html', status=404)
    
    chemicals = model.objects.all()
    return render(request, 'list_chemicals.html', {'chemicals': chemicals, 'model_name': model_name})

@login_required
def checkinandout(request):
    return render(request, 'checkinandout.html')    

@login_required
def print_page(request):
    """Render the page with the download button."""
    return render(request, 'print.html')

@login_required
def generate_qr_pdf_view(request):
    return generate_qr_pdf()

@login_required
def log(request):
    Log_entries = Log.objects.all()
    return render(request, 'log.html', {'log': Log_entries})