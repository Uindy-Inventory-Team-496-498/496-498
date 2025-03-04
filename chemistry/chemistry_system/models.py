from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Sum  # Add this import

def get_model_by_name(model_name):
    model_mapping = {
        'currentlyinstoragetable': (currentlyInStorageTable, [
            'chemBottleIDNUM', 'chemAssociated',
            'chemAmountInBottle', 'chemLocationRoom', 
            'chemLocationCabinet', 'chemLocationShelf'
        ]),
        'allchemicalstable': (allChemicalsTable, [
            'chemID', 'chemMaterial', 'chemName', 'chemConcentration', 
            'chemAmountUnit', 'chemLocationRoom', 
            'chemLocationCabinet', 'chemLocationShelf', 'chemSDS', 'chemNotes', 
            'chemInstrument', 'chemManufacturerBarcode'
        ]),
    }
    return model_mapping.get(model_name.lower())

class allChemicalsTable(models.Model):
    chemID = models.IntegerField(primary_key=True)
    chemMaterial = models.CharField(max_length=255) 
    chemName = models.CharField(max_length=255)
    chemLocationRoom = models.CharField(max_length=255, default="None")
    chemLocationCabinet = models.CharField(max_length=255, default="None")
    chemLocationShelf = models.CharField(max_length=255, default="None")
    chemAmountTotal = models.CharField(max_length=255, default="0")
    chemAmountUnit = models.CharField(null = True, max_length=255)
    chemConcentration = models.CharField(null = True, max_length=255)
    chemSDS = models.CharField(null = True, max_length=20)
    chemNotes = models.CharField(null = True, max_length=255)
    chemInstrument = models.CharField(null = True, max_length=255)
    chemManufacturerBarcode = models.CharField(max_length=255, default="None")

    def __str__(self):
        return self.chemName

    def update_total_amount(self):
        total_amount = currentlyInStorageTable.objects.filter(chemAssociated=self).aggregate(Sum('chemAmountInBottle'))['chemAmountInBottle__sum'] or 0
        self.chemAmountTotal = total_amount
        self.save()
        
class currentlyInStorageTable(models.Model):
    chemBottleIDNUM = models.IntegerField(primary_key=True)
    chemAssociated = models.ForeignKey(allChemicalsTable, on_delete=models.CASCADE, default=1)
    chemLocationRoom = models.CharField(max_length=255, default="None")
    chemLocationCabinet = models.CharField(max_length=255, default="None")
    chemLocationShelf = models.CharField(max_length=255, default="None")
    chemAmountInBottle = models.CharField(max_length=255, default="0")
    chemCheckedOut = models.BooleanField(default=False)
    chemCheckedOutBy = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    chemCheckedOutDate = models.DateTimeField(null=True, blank=True)

class QRCodeData(models.Model):
    qr_code = models.CharField(max_length=255, unique=True)  # Field to store the QR code data
    name = models.CharField(max_length=255)  # Example additional field
    description = models.TextField(blank=True, null=True)  # Example additional field

    def __str__(self):
        return self.name
    
class Log(models.Model):
    user = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.action
