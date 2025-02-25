from .models import allChemicalsTable, currentlyInStorageTable
from django.db.models import Sum

def update_total_amounts():
    # Aggregate the total amounts for each chemical in currentlyInStorageTable
    total_amounts = currentlyInStorageTable.objects.values('chemAssociated').annotate(total=Sum('chemAmountInBottle'))

    # Create a dictionary for quick lookup
    total_amounts_dict = {item['chemAssociated']: item['total'] for item in total_amounts}

    # Update the total amounts in allChemicalsTable
    chemicals = allChemicalsTable.objects.all()
    for chemical in chemicals:
        chemical.chemAmountTotal = total_amounts_dict.get(chemical.chemID, 0)
        chemical.save()