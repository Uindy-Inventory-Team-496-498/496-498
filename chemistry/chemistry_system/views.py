from django.views.generic import ListView
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator

from chemistry_system.models import allChemicals, individualChemicals, Log, get_model_by_name
from .forms import CustomLoginForm, get_dynamic_form, CurrChemicalForm, AllChemicalForm
from .utils import logCall, generate_qr_pdf, populate_storage
from .filters import ChemicalFilter

from dal import autocomplete
from PIL import Image, ImageDraw, ImageFont
from django.http import Http404

def chem_display(request, table_name):
    model_class = get_model_by_name(table_name)
    if not model_class:
        raise Http404(f"Table '{table_name}' does not exist.")
    
    model, _ = model_class  # Extract the model class
    chemMaterials = request.GET.getlist("chemMaterial")
    ChemLocationRoom = request.GET.getlist("chemLocationRoom")
    entries_per_page = request.GET.get("entries_per_page", "10")  # Default to "10"
    
    try:
        entries_per_page = int(entries_per_page) if entries_per_page != "all" else "all"
    except ValueError:
        entries_per_page = 10  # Fallback to default if invalid

    chemicals = model.objects.all()

    if chemMaterials:
        chemicals = chemicals.filter(chemMaterial__in=chemMaterials)
    if ChemLocationRoom:
        chemicals = chemicals.filter(chemLocationRoom__in=ChemLocationRoom)

    if entries_per_page == "all":
        paginator = Paginator(chemicals, chemicals.count())  # Show all items
    else:
        paginator = Paginator(chemicals, entries_per_page)

    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Fetch distinct values for filters
    distinct_materials = model.objects.values_list('chemMaterial', flat=True).distinct()
    distinct_locations = model.objects.values_list('chemLocationRoom', flat=True).distinct()

    context = {
        "page_obj": page_obj,
        "chemical_count": chemicals.count(),
        "distinct_materials": distinct_materials,
        "distinct_locations": distinct_locations,
        "entries_per_page": entries_per_page,
        "table_name": table_name,  # Pass table_name to the context
    }

    if 'HX-Request' in request.headers:
        return render(request, 'cotton/chem_list.html', context)

    return render(request, "chem_display.html", context)

def show_all_chemicals(request):
    context = {}

    filtered_chemicals = ChemicalFilter(
        request.GET, 
        queryset=allChemicals.objects.all()
    )

    context['filtered_chemicals'] = filtered_chemicals

    paginated_filtered_chemicals = Paginator(filtered_chemicals.qs, 5)
    page_number = request.GET.get('page')
    page_obj = paginated_filtered_chemicals.get_page(page_number)

    context['page_obj'] = page_obj

    return render(request, 'show_all_chemicals.html', context)

class ChemicalAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = allChemicals.objects.all()

        if self.q:
            qs = qs.filter(
                Q(chemName__icontains=self.q) |
                Q(chemConcentration__icontains=self.q)
            )
        
        return (qs)
    
    def get_result_label(self, item):
        """Function that defines how the results appear in the dropdown"""
        return f"{item.chemName} ({item.chemConcentration})"
    
class ChemListView(LoginRequiredMixin, ListView):
    """Renders the home page, with a list of all messages."""
    model = individualChemicals

    def get_context_data(self, **kwargs):
        context = super(ChemListView, self).get_context_data(**kwargs)
        return context

@login_required
def currchemicals(request):
    query = request.GET.get('query', '').strip()
    message = None

    if query:
        chemical_list_db = individualChemicals.objects.filter(
            Q(chemAssociated__chemName__icontains=query) |
            Q(chemBottleIDNUM__icontains=query)
        )
        if not chemical_list_db.exists():
            message = "No results found."
    else:
        chemical_list_db = individualChemicals.objects.all()

    chemical_types = allChemicals.objects.values_list('chemMaterial', flat=True).distinct()
    chemical_locations = individualChemicals.objects.values_list('chemLocationRoom', flat=True).distinct()

    # Get the number of entries per page from the request, default to 10
    entries_per_page = request.GET.get('entries_per_page', 10)
    if entries_per_page == 'all':
        entries_per_page = len(chemical_list_db)
    else:
        entries_per_page = int(entries_per_page)

    # Paginate
    paginator = Paginator(chemical_list_db, entries_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'currchemicals.html', {
        'chemical_list_db': page_obj,
        'chemical_types': chemical_types,
        'chemical_locations': chemical_locations,
        'query': query,
        'message': message,
        'entries_per_page': entries_per_page,
        'total_entries': paginator.count
    })

@login_required
def allchemicals(request):
    force_update_total_amount()  # Update total amounts before rendering
    chemical_list_db = allChemicals.objects.all()
    chemical_types = allChemicals.objects.values_list('chemMaterial', flat=True).distinct()
    chemical_locations = allChemicals.objects.values_list('chemLocationRoom', flat=True).distinct()

    # Get the number of entries per page from the request, default to 10
    entries_per_page = request.GET.get('entries_per_page', 10)
    if entries_per_page == 'all':
        entries_per_page = len(chemical_list_db)
    else:
        entries_per_page = int(entries_per_page)

    # Paginate
    paginator = Paginator(chemical_list_db, entries_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'all_chemicals.html', {
        'chemical_list_db': page_obj,
        'chemical_types': chemical_types,
        'chemical_locations': chemical_locations,
        'entries_per_page': entries_per_page,
        'total_entries': paginator.count
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
    results = individualChemicals.objects.none()
    message = None

    if query:
        if query.isdigit():
            # If user typed only digits, match bottle ID EXACTLY (no name match).
            results = individualChemicals.objects.filter(
                chemBottleIDNUM__iexact=query
            )
        else:
            # If query is non-numeric, match names by partial or startswith, etc.
            results = individualChemicals.objects.filter(
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
        matches = individualChemicals.objects.filter(
            Q(chemAssociated__chemName__istartswith=query) | Q(chemBottleIDNUM__iexact=query)
        )
    else:
        # If it's non-numeric, match only names that start with the query.
        matches = individualChemicals.objects.filter(
            Q(chemAssociated__chemName__istartswith=query)
        )
    
    data = [
        {'chemName': m.chemAssociated.chemName, 'chemBottleIDNUM': m.chemBottleIDNUM}
        for m in matches
    ]
    return JsonResponse(data, safe=False)

@login_required
def add_chemical(request, model_name):
    return_value = ""
    if model_name.lower() == 'individualChemicals':
        form_class = CurrChemicalForm
        return_value = "currchemicals"
    elif model_name.lower() == 'allChemicals':
        form_class = AllChemicalForm
        return_value = "allchemicals"
    else:
        form_class = get_dynamic_form(model_name)

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            logCall(request.user.username, f"Added chemical to {model_name}")
            messages.success(request, 'Chemical added successfully!')
            return redirect(return_value)
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
        model_name = request.POST.get('model_name', 'individualChemicals')
        model_class, _ = get_model_by_name(model_name)
        
        if model_class:
            row_count = model_class.objects.count()
            model_class.objects.all().delete()
            logCall(request.user.username, f"Deleted {row_count} rows from {model_name}")
            messages.success(request, 'All chemicals have been deleted successfully!')
        else:
            messages.error(request, 'Invalid model name.')

        return redirect('currchemicals' if model_name == 'individualChemicals' else 'allchemicals')
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

    

def generate_qr_pdf_view(request):
    return generate_qr_pdf(request)


@login_required
def log(request): # DONT MODIFY THIS FUNCTION
    query = request.GET.get('search', '')
    query_date = request.GET.get('date', '')
    log_entries = Log.objects.all().order_by('-date')  # Fetch logs ordered by date
    if query_date:
        print("WORKING")
        log_entries = log_entries.filter(
            date__icontains=query_date  ## DONT MODIFY THIS LINE
        )
    if query:
        log_entries = log_entries.filter(
            user__icontains=query  # DONT MODIFY THIS LINE
        ) | log_entries.filter(
            action__icontains=query  # DONT MODIFY THIS LINE
        ) | log_entries.filter(
            date__icontains=query  # DONT MODIFY THIS LINE
        )
    
    
    paginator = Paginator(log_entries, 25)  # Show 10 logs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)  # Get the requested page

    return render(request, 'log.html', {'page_obj': page_obj, 'query': query})  

@login_required
def run_populate_storage(request):
    populate_storage()
    messages.success(request, 'Database populated with dummy data successfully!')
    return redirect(request.META.get('HTTP_REFERER', '/'))  # Redirect to the referring page

@login_required
def force_update_total_amount(request):
    chemicals = allChemicals.objects.all()
    for chemical in chemicals:
        chemical.update_total_amount()
    messages.success(request, 'Total amounts updated for all chemicals successfully!')
    return redirect('chem_display')