import qrcode
import io
import random
import csv
from datetime import datetime
import os
import pytz


from PIL import Image, ImageDraw, ImageFont
from django.contrib import messages
from django.db.models import Sum
from django.utils.timezone import now
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from .models import allChemicals, individualChemicals, Log, get_model_by_name
from .forms import CSVUploadForm
from datetime import timedelta

def logCall(user: str, action: str):
    try:
        date = datetime.now()
        date = date - timedelta(hours=5)
        log_add = Log(user=user, action=action, date=date)
        log_add.save()
        print(f"Log entry saved: {user} - {action}")  # Debugging print statement
    except Exception as e:
        print(f"Logging error: {e}")  # Print errors for debugging

def logCall(user: str, action: str):
    try:
        date = now()
        log_add = Log(user=user, action=action, date=date)
        log_add.save()
        print(f"Log entry saved: {user} - {action}")  # Debugging print statement
    except Exception as e:
        print(f"Logging error: {e}")  # Print errors for debugging

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
        number = random.randint(0, 12000000000)
        data = "https://csci06.is.uindy.edu/" + str(number)  # Unique data for each QR code
        qr = qrcode.QRCode(box_size=5, border=0)  # Adjust size
        qr.add_data(data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill="black", back_color="white").resize((qr_size, qr_size))

        # Compute position with margins
        

        # Paste QR code on canvas
        canvas.paste(qr_img, (current_x-150, current_y-150))

        # Draw text on canvas
        position = (current_x-50, current_y + 175)
        draw.text(position, str(number), font=font, fill="black")


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

def export_chemicals_csv(request):
    model_name = request.GET.get('model_name', 'individualChemicals')
    model_class, required_fields = get_model_by_name(model_name)
    
    if not model_class:
        messages.error(request, 'Invalid model name.')
        return redirect('currchemicals' if model_name == 'individualChemicals' else 'allchemicals')

    chemicals = model_class.objects.all()
    response = HttpResponse(content_type='text/csv')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="{model_name}_{timestamp}.csv"'

    writer = csv.writer(response)
    writer.writerow(required_fields)

    row_count = 0
    for chemical in chemicals:
        row = []
        for field in required_fields:
            if field == 'chemAssociated':
                row.append(getattr(chemical, 'chemAssociated_id'))
            else:
                row.append(getattr(chemical, field))
        writer.writerow(row)
        row_count += 1

    logCall(request.user.username, f"Exported {row_count} rows from {model_name}")
    return response

@require_POST
def import_chemicals_csv(request):
    print("Importing chemicals CSV...")  # Debugging print statement
    form = CSVUploadForm(request.POST, request.FILES)
    model_name = request.POST.get('model_name', '').lower()
    model_class, required_fields = get_model_by_name(model_name)

    if form.is_valid() and model_class:
        print(f"Form is valid. Importing into model: {model_name}")
        csv_file = request.FILES['file']
        reader = csv.DictReader(csv_file.read().decode('utf-8').splitlines())

        # Get all field names from the model
        model_fields = [field.name for field in model_class._meta.get_fields()]
        print(f"Model fields: {model_fields}")

        row_count = 0
        for row in reader:
            try:
                # Filter out columns that are not in the model fields
                filtered_data = {key: value for key, value in row.items() if key in model_fields}
                #print(f"Filtered data: {filtered_data}")

                # Handle the foreign key relationship for `chemAssociated` in `individualChemicals`
                if model_name == 'individualchemicals' and 'chemAssociated' in filtered_data:
                    try:
                        associated_chemical = allChemicals.objects.get(pk=filtered_data['chemAssociated'])
                        filtered_data['chemAssociated'] = associated_chemical
                    except allChemicals.DoesNotExist:
                        print(f"Associated chemical with ID {filtered_data['chemAssociated']} does not exist.")
                        messages.error(request, f"Associated chemical with ID {filtered_data['chemAssociated']} does not exist.")
                        continue

                # Use the first required field as the unique identifier (e.g., primary key)
                id_field = required_fields[0]
                if id_field not in filtered_data:
                    raise KeyError(f"Missing required field: {id_field}")

                # Update or create the record in the database
                model_class.objects.update_or_create(
                    **{id_field: filtered_data[id_field]},
                    defaults=filtered_data
                )
                row_count += 1
            except Exception as e:
                # Log only exceptions
                #print(f"Error saving row: {row}. Exception: {e}")
                messages.error(request, f"Error saving row: {row}. Exception: {e}")
                continue

        logCall(request.user.username, f"Imported {row_count} rows into {model_name}")
        messages.success(request, f"Successfully imported {row_count} rows into {model_name}.")
    else:
        messages.error(request, 'Failed to import chemicals. Please check the file format.')

    return redirect(request.META.get('HTTP_REFERER', '/'))

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
        logCall(request.user.username, f"Checked in chemical with QR ID: {qrcode_value}")
    else:
        chemical_instance.chemCheckedOut = True
        chemical_instance.chemCheckedOutBy = request.user
        chemical_instance.chemCheckedOutDate = now()
        message = f"Chemical successfully checked out by {request.user.username} at {chemical_instance.chemCheckedOutDate.strftime('%Y-%m-%d %H:%M:%S')}."
        logCall(request.user.username, f"Checked out chemical with QR ID: {qrcode_value}")
    
    # Save the updated chemical instance
    chemical_instance.save()
    
    return JsonResponse({"message": message})

def populate_storage():
    # Clear existing data
    individualChemicals.objects.all().delete()

    # Get all chemical records
    all_chemicals = list(allChemicals.objects.all())

    # Generate dummy data
    bottle_id = 1
    for chem in all_chemicals:
        for _ in range(1):  # Create x bottles for each chemical
            individualChemicals.objects.create(
                chemBottleIDNUM=bottle_id,
                chemAssociated=chem,
                chemLocationRoom=chem.chemLocationRoom,
                chemLocationCabinet=random.choice(['Cabinet A', 'Cabinet B', 'Cabinet C']),
                chemLocationShelf=random.choice(['Shelf 1', 'Shelf 2', 'Shelf 3']),
                chemAmountInBottle=f"{random.randint(1, 1000)}",
            )
            bottle_id += 1