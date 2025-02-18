import re
from chemistry_system.models import QRCodeData, currentlyInStorageTable, allChemicalsTable, get_model_by_name
from django.views.generic import ListView
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .forms import CustomLoginForm, get_dynamic_form, CSVUploadForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
import csv
from django.views.decorators.http import require_POST
from django.utils.timezone import now
from django.core.paginator import Paginator


class ChemListView(LoginRequiredMixin,ListView):
    """Renders the home page, with a list of all messages."""
    model = currentlyInStorageTable

    def get_context_data(self, **kwargs):
        context = super(ChemListView, self).get_context_data(**kwargs)
        return context

@login_required
def currchemicals(request):
    chemical_list_db = currentlyInStorageTable.objects.all()
    chemical_types = currentlyInStorageTable.objects.values_list('chemMaterial', flat=True).distinct()
    chemical_locations = currentlyInStorageTable.objects.values_list('chemLocationRoom', flat=True).distinct()
    #chemical_locations = ['None' if location == '' else location for location in chemical_locations]

    return render(request, 'currchemicals.html', {
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
def update_checkout_status(request, model_name, qrcode_value):
    try:
        model_class, _ = get_model_by_name(model_name)
        if model_class is None:
            raise ValueError("Model not found for the given model name.")
        
        # Query the chemical in the storage table based on qrcodeValue
        chemical_instance = model_class.objects.get(chemBottleIDNUM=qrcode_value)
    
    except model_class.DoesNotExist:
        return JsonResponse({"message": f"Chemical with QR code {qrcode_value} not found."}, status=404)
    
    # Toggle the checkout status
    if chemical_instance.chemCheckedOut:
        chemical_instance.chemCheckedOut = False
        chemical_instance.chemCheckedOutBy = None
        chemical_instance.chemCheckedOutDate = None
        message = f"Chemical successfully checked in by {request.user.username} at {now().strftime('%Y-%m-%d %H:%M:%S')}."
    else:
        chemical_instance.chemCheckedOut = True
        chemical_instance.chemCheckedOutBy = request.user
        chemical_instance.chemCheckedOutDate = now()
        message = f"Chemical successfully checked out by {request.user.username} at {chemical_instance.chemCheckedOutDate.strftime('%Y-%m-%d %H:%M:%S')}."
    
    # Save the updated chemical instance
    chemical_instance.save()
    
    return JsonResponse({"message": message})


@login_required
def search_by_qr(request):
    qr_code_value = request.GET.get('chem_id')

    if not qr_code_value:
        return JsonResponse({'error': 'chem_id is required'}, status=400)

    # Perform the search based on chemBottleIDNUM
    try:
        results = currentlyInStorageTable.objects.filter(
            chemBottleIDNUM__icontains=qr_code_value
        )

        if not results.exists():
            return JsonResponse({'message': 'No results found'}, status=404)

        # Assuming you want to return the first matching record, adjust this as needed
        result = results.first()

        # Prepare data to return
        response_data = {
            'chemName': result.chemName,
            'chemBottleIDNUM': result.chemBottleIDNUM,
            "chemCheckedOut": result.chemCheckedOut,
        }
        return JsonResponse(response_data, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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
                chemName__icontains=query
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

    # If the user typed only digits, do exact match on ID; otherwise do 'starts with' on chemName.
    if query.isdigit():
        # We want ID == query OR name starts with query (in case you still want name matches).
        matches = currentlyInStorageTable.objects.filter(
            Q(chemName__istartswith=query) | Q(chemBottleIDNUM__iexact=query)
        )
    else:
        # If it's non-numeric, match only names that start with the query.
        matches = currentlyInStorageTable.objects.filter(
            chemName__istartswith=query
        )
    
    data = [
        {'chemName': m.chemName, 'chemBottleIDNUM': m.chemBottleIDNUM}
        for m in matches
    ]
    return JsonResponse(data, safe=False)


@login_required
def add_chemical(request, model_name):
    DynamicChemicalForm = get_dynamic_form(model_name)
    if request.method == 'POST':
        form = DynamicChemicalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Chemical added successfully!')
            return redirect('currchemicals')
    else:
        form = DynamicChemicalForm()

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
        messages.success(request, 'Chemical deleted successfully!')
        return redirect('currchemicals')
    
    return render(request, 'confirm_delete.html', {'chemical': chemical})

@login_required
def delete_all_chemicals(request):
    if request.method == 'POST':
        currentlyInStorageTable.objects.all().delete()
        messages.success(request, 'All chemicals have been deleted successfully!')
        return redirect('currchemicals')
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
def export_chemicals_csv(request):
    chemicals = currentlyInStorageTable.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="chemicals.csv"'

    writer = csv.writer(response)
    writer.writerow(['chemBottleIDNUM', 'chemMaterial', 'chemName', 'chemLocationRoom', 'chemLocationCabinet', 'chemLocationShelf', 
        'chemAmountInBottle', 'chemAmountUnit', 'chemConcentration', 'chemSDS', 'chemNotes', 'chemInstrument'])

    for chemical in chemicals:
        writer.writerow([
            chemical.chemBottleIDNUM,
            chemical.chemMaterial,
            chemical.chemName,
            chemical.chemLocationRoom,
            chemical.chemLocationCabinet,
            chemical.chemLocationShelf,
            chemical.chemAmountInBottle,
            chemical.chemAmountUnit,
            chemical.chemConcentration,
            chemical.chemSDS,
            chemical.chemNotes,
            chemical.chemInstrument
        ])

    return response

@login_required
@require_POST
def import_chemicals_csv(request):
    form = CSVUploadForm(request.POST, request.FILES)
    if form.is_valid():
        csv_file = request.FILES['file']
        reader = csv.DictReader(csv_file.read().decode('utf-8').splitlines())
        
        for row in reader:
            currentlyInStorageTable.objects.update_or_create(
                chemBottleIDNUM=row['chemBottleIDNUM'],
                defaults={
                    'chemMaterial': row['chemMaterial'],
                    'chemName': row['chemName'],
                    'chemConcentration': row['chemConcentration'],
                    'chemAmountInBottle': row['chemAmountInBottle'],
                    'chemAmountUnit': row['chemAmountUnit'],
                    'chemLocationRoom': row['chemLocationRoom'],
                    'chemLocationCabinet': row['chemLocationCabinet'],
                    'chemLocationShelf': row['chemLocationShelf'],
                    'chemSDS': row['chemSDS'],
                    'chemNotes': row['chemNotes'],
                    'chemInstrument': row['chemInstrument']
                }
            )
        messages.success(request, 'Chemicals imported successfully!')
    else:
        messages.error(request, 'Failed to import chemicals. Please check the file format.')

    return redirect('currchemicals')

@login_required
def checkinandout(request):
    return render(request, 'checkinandout.html')    