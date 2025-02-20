import re
from chemistry_system.models import QRCodeData, allChemicalsTable, currentlyInStorageTable, get_model_by_name, Log
from django.views.generic import ListView
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .forms import CustomLoginForm, get_dynamic_form, CSVUploadForm, CurrChemicalForm, AllChemicalForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
import csv
from django.views.decorators.http import require_POST
from django.utils.timezone import now
from django.core.paginator import Paginator
from PIL import Image, ImageDraw
import qrcode
import io
import random
import os

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
def update_checkout_status(request, model_name, qrcode_value):
    try:
        model_class, _ = get_model_by_name(model_name)
        if (model_class is None):
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
        logCall(request.user.username, f"Checked in chemical with QR code {qrcode_value}")
    else:
        chemical_instance.chemCheckedOut = True
        chemical_instance.chemCheckedOutBy = request.user
        chemical_instance.chemCheckedOutDate = now()
        message = f"Chemical successfully checked out by {request.user.username} at {chemical_instance.chemCheckedOutDate.strftime('%Y-%m-%d %H:%M:%S')}."
        logCall(request.user.username, f"Checked out chemical with QR code {qrcode_value}")
    
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
    return_value = ""
    if model_name.lower() == 'currentlyinstoragetable':
        form_class = CurrChemicalForm
        return_value = "currchemicals"
    elif model_name.lower() == 'allchemicalstable':
        form_class = AllChemicalForm
        return_value = "allchemicals"
    else:
        form_class = get_dynamic_form(model_name)

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
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
    model_name = request.GET.get('model_name', 'currentlyinstoragetable')
    model_class, required_fields = get_model_by_name(model_name)
    
    if not model_class:
        messages.error(request, 'Invalid model name.')
        return redirect('currchemicals' if model_name == 'currentlyinstoragetable' else 'allchemicals')

    chemicals = model_class.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{model_name}.csv"'

    writer = csv.writer(response)
    writer.writerow(required_fields)

    for chemical in chemicals:
        row = []
        for field in required_fields:
            if field == 'chemAssociated':
                row.append(getattr(chemical, 'chemAssociated_id'))
            else:
                row.append(getattr(chemical, field))
        writer.writerow(row)

    return response

@login_required
@require_POST
def import_chemicals_csv(request):
    form = CSVUploadForm(request.POST, request.FILES)
    model_name = request.POST.get('model_name', 'currentlyinstoragetable')
    model_class, required_fields = get_model_by_name(model_name)
    
    if form.is_valid() and model_class:
        csv_file = request.FILES['file']
        reader = csv.DictReader(csv_file.read().decode('utf-8').splitlines())
        
        id_field = required_fields[0]  # Use the first required field as the ID field
        
        for row in reader:
            try:
                defaults = {field: row[field] for field in row if field in required_fields}
                
                if 'chemAssociated' in defaults:
                    try:
                        defaults['chemAssociated'] = allChemicalsTable.objects.get(pk=defaults['chemAssociated'])
                    except allChemicalsTable.DoesNotExist:
                        messages.error(request, f"Chemical with ID {defaults['chemAssociated']} does not exist in allChemicalsTable.")
                        continue
                
                model_class.objects.update_or_create(
                    **{id_field: row[id_field]},
                    defaults=defaults
                )
            except KeyError as e:
                messages.error(request, f"Missing field in CSV: {e}")
                return redirect('currchemicals' if model_name == 'currentlyinstoragetable' else 'allchemicals')
            except Exception as e:
                messages.error(request, f"Error importing row: {e}")
                return redirect('currchemicals' if model_name == 'currentlyinstoragetable' else 'allchemicals')
        
        messages.success(request, 'Chemicals imported successfully!')
    else:
        messages.error(request, 'Failed to import chemicals. Please check the file format.')

    return redirect('currchemicals' if model_name == 'currentlyinstoragetable' else 'allchemicals')

@login_required
def checkinandout(request):
    return render(request, 'checkinandout.html')    

@login_required
def print_page(request):
    """Render the page with the download button."""
    return render(request, 'print.html')

@login_required
def generate_qr_pdf(request):
    num_qr = 24  # Number of QR codes
    cols = 4  # Number of columns
    rows = 6   # Number of rows (num_qr / cols)
    qr_size = 300  # Size of each QR code in pixels

    # Calculate canvas size (including margins)
    dpi = 300  
    canvas_width = 8.5 * dpi  
    canvas_height = 11 * dpi  
    canvas_size = (int(canvas_width), int(canvas_height))

    # Create a blank canvas
    canvas = Image.new("RGB", canvas_size, "white")
    draw = ImageDraw.Draw(canvas)

    first_x = 384+40
    first_y = 250
    between_x = 565
    between_y = 565
    num_so_far = 0

    current_x = first_x
    current_y = first_y

    current_directory = os.path.dirname(os.path.realpath(__file__))

    font_path = os.path.join(current_directory, "tnr.ttf")  # Replace with your font file name
    font_size = 24  # Adjust the font size here
    font = ImageFont.truetype(font_path, font_size)
    # Generate and place QR codes
    for i in range(num_qr):
        if num_so_far % cols == 0 and num_so_far != 0:
            current_x = first_x
            current_y += between_y
        num_so_far += 1
        data = random.randint(0, 12000000000)  # Unique data for each QR code
        qr = qrcode.QRCode(box_size=5, border=0)  # Adjust size
        qr.add_data(data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill="black", back_color="white").resize((qr_size, qr_size))

        # Compute position with margins
        

        # Paste QR code on canvas
        canvas.paste(qr_img, (current_x-150, current_y-150))

        # Draw text on canvas
        position = (current_x-50, current_y + 175)
        draw.text(position, data, font=font, fill="black")

        # Update position for next QR code
        current_x += between_x

        

    # trim the right side of the image
    canvas = canvas.crop((0, 0, canvas_width, canvas_height))
    # set image size to 9*11 inches
    canvas = canvas.resize((int(9*300), int(11*300)))

    pdf_buffer = io.BytesIO()
    canvas.save(pdf_buffer, format="PDF")
    pdf_buffer.seek(0)

    # Return as a response
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="qr_codes.pdf"'
    return response

@login_required
def log(request):
    Log_entries = Log.objects.all()
    return render(request, 'log.html', {'log': Log_entries})

def logCall(user: str, action: str):
    try:
        date = now()
        log_add = Log(user=user, action=action, date=date)
        log_add.save()
        print(f"Log entry saved: {user} - {action}")  # Debugging print statement
    except Exception as e:
        print(f"Logging error: {e}")  # Print errors for debugging