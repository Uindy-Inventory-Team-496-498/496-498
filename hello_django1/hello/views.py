import re
from hello.models import QRCodeData, currentlyInStorageTable, allChemicalsTable, get_model_by_name
from django.views.generic import ListView
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .forms import CustomLoginForm, get_dynamic_form
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib import messages
from django.template import loader
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

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
def contact(request):
    return render(request, "contact.html")

@login_required
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

@login_required
def delete_chemical(request, chemBottleIDNUM):
    chemical = get_object_or_404(currentlyInStorageTable, chemBottleIDNUM=chemBottleIDNUM)

    if request.method == "POST":
        try:
            # Delete the chemical record
            chemical.delete()
            # Redirect to a page, e.g., chemical list or a success message
            return render(request, 'currchemicals.html')
        except Exception as e:
            # Log detailed error information
            print(f"Error deleting chemical with ID {chemBottleIDNUM}: {e}")
            # You can also log this to a file or database if needed
            return JsonResponse({'error': f'Failed to delete the chemical. Error: {str(e)}'}, status=500)
    else:
        return render(request, "scanner_delete")
        

@login_required  
def qr_code_scanner(request):
    return render(request, 'scanner.html')

@login_required
def qr_code_scan(request):
    return render(request, 'scan.html') # Only if you need to disable CSRF for testing


@login_required
def search_by_qr(request):
    qr_code_value = request.GET.get('chem_id')
    try:
        results = currentlyInStorageTable.objects.filter(
            chemBottleIDNUM__icontains=qr_code_value
        )
        result = results.first()
       # chemical = currentlyInStorageTable.objects.get(chemBottleIDNUM=qr_code_value)  # Assuming chemBottleIDNUM is used as ID
        response_data = {
            'chemBottleIDNUM': result.chemBottleIDNUM,  
            'chemName': result.chemName,
            'chemLocationCabinet': result.chemLocationCabinet,
            'chemLocationShelf': result.chemLocationShelf,
            'chemAmountInBottle': result.chemAmountInBottle,
            'chemStorageType': result.chemStorageType,
            "chemCheckedOut": result.chemCheckedOut,
        }
        return JsonResponse(response_data, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@login_required
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
@login_required
def basic_search(request):
    query = request.GET.get('query', '')  # Get the search term from the request
    results = currentlyInStorageTable.objects.filter(
        chemBottleIDNUM__icontains=query
    ) | currentlyInStorageTable.objects.filter(
        chemName__icontains=query
    ) | currentlyInStorageTable.objects.filter( chemAmountUnit_icontains=query)  # Search by ID or name using icontains for partial matches
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




#this vs search_by_qr_code could cause problems. 
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
def add_chemical(request, model_name):
    DynamicChemicalForm = get_dynamic_form(model_name)
    if request.method == 'POST':
        form = DynamicChemicalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Chemical added successfully!')
            return redirect('currchemicals')
    else:
        # Create the form with the existing chemical data pre-filled
        form = EditChemicalForm(instance=chemical)
    return render(request, 'edit_chemical.html', {'form': form, 'chemical': chemical})

@login_required
def scanner_delete(request):
    return render(request, 'scanner_delete.html')

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



"""below is delete_chemical from main (i think from nicks check in & out branch)"""

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
