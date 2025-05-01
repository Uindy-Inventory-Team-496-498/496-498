import json
import re
from django.views.generic import ListView
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator
from django.urls import reverse
from django.db import models  

from chemistry_system.models import allChemicals, individualChemicals, Log, get_model_by_name
from .forms import CustomLoginForm, get_dynamic_form, IndividualChemicalsForm, AllChemicalForm
from .utils import logCall, generate_qr_pdf, populate_storage

from dal import autocomplete # type: ignore
from PIL import Image, ImageDraw, ImageFont # type: ignore

def admin_dashboard(request):
    return HttpResponse("<h1> Admin Dashboard </h1>")

@login_required
def chem_display(request, table_name):
    model_class = get_model_by_name(table_name)
    if not model_class:
        raise Http404(f"Table '{table_name}' does not exist.")
    
    model, _ = model_class  # Extract the model class
    chemMaterials = request.GET.getlist("chemMaterial")
    chemLocationRoom = request.GET.getlist("chemLocationRoom")
    entries_per_page = request.GET.get("entries_per_page", "10")  # Default to "10"
    sort_by = request.GET.get("sort_by", "")  # Get the sort_by parameter


    try:
        entries_per_page = int(entries_per_page) if entries_per_page != "all" else "all"
    except ValueError:
        entries_per_page = 10  # Fallback to default if invalid

    chemicals = model.objects.all()

    if chemMaterials:
        chemicals = chemicals.filter(chemMaterial__in=chemMaterials)
    if chemLocationRoom:
        chemicals = chemicals.filter(chemLocationRoom__in=chemLocationRoom)
    
    if table_name == "allChemicals":
        if sort_by == "chemAmountAsc":
            chemicals = chemicals.order_by("chemAmountPercentage")
        elif sort_by == "chemAmountDesc":
            chemicals = chemicals.order_by("-chemAmountPercentage")

    if table_name == "individualChemicals":
        if sort_by == "chemAmountAsc":
            chemicals = chemicals.order_by("chemAmountInBottle")
        elif sort_by == "chemAmountDesc":
            chemicals = chemicals.order_by("-chemAmountInBottle")

    # Calculate counts for each filter option based on the filtered queryset
    material_counts = chemicals.values('chemMaterial').annotate(count=models.Count('chemMaterial'))
    location_counts = chemicals.values('chemLocationRoom').annotate(count=models.Count('chemLocationRoom'))

    # Convert counts to dictionaries for easier access in the template
    material_dict = {item['chemMaterial']: item['count'] for item in material_counts}
    location_dict = {item['chemLocationRoom']: item['count'] for item in location_counts}

    if entries_per_page == "all":
        paginator = Paginator(chemicals, chemicals.count())  # Show all items
    else:
        paginator = Paginator(chemicals, entries_per_page)

    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    target_id = "chem-list" if table_name == "allChemicals" else "chem-list-indiv"
    target_html = "chem_list" if table_name == "allChemicals" else "chem_list_indiv"

    context = {
        "page_obj": page_obj,
        "chemical_count": chemicals.count(),
        "entries_per_page": entries_per_page,
        "table_name": table_name,  # Pass table_name to the context
        "material_dict": material_dict,
        "location_dict": location_dict,
        "target_id": target_id,
        "sort_by": sort_by, 
    }

    if 'HX-Request' in request.headers:
        #print("-------------------------" + request.htmx.target  + "-------------------------")
        if request.htmx.target == target_id:
            return render(request, f"cotton/{target_html}.html", context)
        
    return render(request, "chem_display.html", context)

class ChemicalAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = allChemicals.objects.all()

        if self.q:
            qs = qs.filter(
                Q(chemName__icontains=self.q) | 
                Q(chemConcentration__icontains=self.q) |
                Q(chemMaterial__icontains=self.q)
            )
        
        return (qs)
    
    def get_result_label(self, item):
        """Function that defines how the results appear in the dropdown"""
        return f"{item.chemName} {item.chemMaterial} ({item.chemConcentration})"
    
class ChemListView(LoginRequiredMixin, ListView):
    """Renders the home page, with a list of all messages."""
    model = individualChemicals

    def get_context_data(self, **kwargs):
        context = super(ChemListView, self).get_context_data(**kwargs)
        return context


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
def home(request, value="0"):
    return render(request, "home.html")

@login_required
def qr_code_scan(request):
    return render(request, 'scan.html') # Only if you need to disable CSRF for testing

@login_required
def search_page(request):
    query = request.GET.get('query', '').strip()
    model_name = request.GET.get('model', 'individualChemicals')  # Default to individualChemicals
    message = None

    # Determine the model to query based on the model parameter
    if model_name == 'allChemicals':
        model = allChemicals
    else:
        model = individualChemicals

    # Initialize results as an empty queryset
    results = model.objects.none()

    if query:
        if model == allChemicals:
            # Query for allChemicals
            if query.isdigit():
                results = model.objects.filter(
                    chemID__iexact=query
                )
            else:
                results = model.objects.filter(
                    Q(chemName__icontains=query) |
                    Q(chemMaterial__icontains=query)
                )
        else:
            # Query for individualChemicals
            if query.isdigit():
                results = model.objects.filter(
                    chemBottleIDNUM__iexact=query
                )
            else:
                results = model.objects.filter(
                    Q(chemAssociated__chemName__icontains=query)
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
        'model': model_name,
        'message': message,
    })

@login_required
def live_search_api(request):
    query = request.GET.get('q', '').strip()
    model_name = request.GET.get('model', 'none')  # Default to 'none' if not provided
    print(f"model parameter received: {model_name}")  # Debugging

    model_class = get_model_by_name(model_name)
    if not model_class:
        raise Http404(f"model '{model_name}' does not exist.")
    
    model, _ = model_class  # Extract the model class
    if not query:
        return JsonResponse([], safe=False)

    # Determine the model to query based on the model parameter
    if model_name == 'allChemicals':  # Compare model name, not model
        if query.isdigit():
            matches = model.objects.filter(
                Q(chemID__iexact=query)
            )
        else:
            matches = model.objects.filter(
                Q(chemName__icontains=query) |
                Q(chemMaterial__icontains=query)
            )
        data = [
            {'chemName': m.chemName, 'chemID': m.chemID}
            for m in matches
        ]
        
    else:
        if query.isdigit():
            matches = model.objects.filter(
                Q(chemBottleIDNUM__iexact=query)
            )
        else:
            matches = model.objects.filter(
                Q(chemAssociated__chemName__icontains=query)
            )
        
        data = [
            {'chemName': m.chemAssociated.chemName, 'chemBottleIDNUM': m.chemBottleIDNUM}
            for m in matches
        ]
    return JsonResponse(data, safe=False)


@login_required
def add_chemical(request, model_name):
    if model_name.lower() == 'allchemicals':
        form_class = AllChemicalForm
    elif model_name.lower() == 'individualchemicals':
        form_class = IndividualChemicalsForm
    else:
        raise Http404(f"Model '{model_name}' not found.")
    referrer = request.GET.get('referrer', f'/chem_display/{model_name}')
  
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            chemical = form.save()
            logCall(request.user.username, f"Added chemical to {model_name}")
            messages.success(request, 'Chemical added successfully!')
            return redirect(f"/chem_display/{model_name}")
    else:
        form = form_class()

    return render(request, 'add_chemical.html', {'form': form, 'model_name': model_name, 'referrer': referrer})
  
@login_required
def scanner_add(request, model_name):
    referrer = request.META.get('HTTP_REFERER', '/')
    return render(request, 'scanner_add.html', {'model_name': model_name, 'referrer': referrer})

@login_required
def edit_chemical(request, model_name, pk):
    model_class = get_model_by_name(model_name)
    model = model_class[0]
    if not model:
        return render(request, '404.html', status=404)
    
    chemical = get_object_or_404(model, pk=pk)
    DynamicChemicalForm = get_dynamic_form(model_name)
    referrer = request.GET.get('referrer', '/')

    if request.method == 'POST':
        form = DynamicChemicalForm(request.POST, instance=chemical)
        if form.is_valid():
            logCall(request.user.username, f"Updated chemical with ID {pk}")
            form.save()
            messages.success(request, 'Chemical updated successfully!')
            return redirect(referrer)
    else:
        form = DynamicChemicalForm(instance=chemical)

    return render(request, 'edit_chemical.html', {'form': form, 'chemical': chemical, 'model_name': model_name, 'referrer': referrer} )

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
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
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

        return redirect(request.META.get('HTTP_REFERER', '/'))
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
    if 'HX-Request' in request.headers:
        return render(request, 'cotton/amount_ui.html')
    return render(request, 'checkinandout.html')  

@login_required
def update_chemical_amount(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            chem_id = data.get('chem_id')
            used_amount = data.get('amount')
            
            match = re.match(r'([\d.]+)\s*([a-zA-Z]+)?', used_amount)
            
            if not match:
                return JsonResponse({
                    'success': False,
                    'message': "Invalid amount format. Please enter a number followed by units (e.g., 5 mL)."
                }, status=400)
                
            amount_value = float(match.group(1))
            amount_unit = match.group(2) if match.group(2) else ""
            
            model_class, _ = get_model_by_name('individualChemicals')
            if model_class is None:
                raise ValueError("Model not found")
                
            chemical = model_class.objects.get(chemBottleIDNUM=chem_id)
            
            current_amount_str = chemical.chemAmountInBottle 
            current_match = re.match(r'([\d.]+)\s*([a-zA-Z]+)?', current_amount_str)
            
            if not current_match:
                return JsonResponse({
                    'success': False,
                    'message': f"Current amount format is invalid: {current_amount_str}"
                }, status=400)
                
            current_value = float(current_match.group(1))
            current_unit = current_match.group(2) if current_match.group(2) else ""
            
            # Validate units
            if amount_unit.lower() != current_unit.lower():
                return JsonResponse({
                    'success': False,
                    'message': f"Units don't match. Chemical has {current_unit}, but you entered {amount_unit}."
                }, status=400)
                
            new_value = current_value - amount_value
            
            # Validate the new amount isn't negative
            if new_value < 0:
                return JsonResponse({
                    'success': False,
                    'message': f"Used amount ({amount_value} {amount_unit}) exceeds available amount ({current_value} {current_unit})."
                }, status=400)
                
            # Update the amount
            new_amount_str = f"{new_value} {current_unit}"
            chemical.chemAmountInBottle = new_amount_str
            chemical.save()
            logCall(request.user.username, f"Updated amount for chemical {chem_id}: used {used_amount}, remaining {new_amount_str}")
            
            return JsonResponse({
                'success': True,
                'message': f"Chemical checked in. Used: {used_amount}, Remaining: {new_amount_str}"
            })
            
        except model_class.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': f"Chemical with ID {chem_id} not found"
            }, status=404)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': "Method not allowed"
    }, status=405)

@login_required
def get_chemical_details(request, qrcode_value):
    try:
        model_class, _ = get_model_by_name('individualChemicals')
        if model_class is None:
            raise ValueError("Model not found")
        
        chemical = model_class.objects.get(chemBottleIDNUM=qrcode_value)
        
        return JsonResponse({
            'success': True,
            'totalAmount': chemical.chemAmountInBottle,
            'name': getattr(chemical, 'chemName', ''),
            'id': chemical.chemBottleIDNUM
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

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
    return redirect(request.META.get('HTTP_REFERER', '/'))  

@login_required
def force_update_total_amount(request):
    chemicals = allChemicals.objects.all()
    for chemical in chemicals:
        chemical.update_total_amount()
    messages.success(request, 'Total amounts updated for all chemicals successfully!')
    return redirect(request.META.get('HTTP_REFERER', '/'))
