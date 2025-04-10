from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Sum  # Add this import
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

def get_model_by_name(model_name):
    model_mapping = {
        'individualchemicals': (individualChemicals, [
            'chemBottleIDNUM', 'chemAssociated',
            'chemAmountInBottle', 'chemLocationRoom', 
            'chemLocationCabinet', 'chemLocationShelf'
        ]),
        'allchemicals': (allChemicals, [
            'chemID', 'chemMaterial', 'chemName', 'chemConcentration', 
            'chemAmountUnit', 'chemLocationRoom', 
            'chemLocationCabinet', 'chemLocationShelf', 'chemSDS', 'chemNotes', 
            'chemInstrument', 'chemAmountExpected'  
        ]),
    }
    return model_mapping.get(model_name.lower())  # Ensure case-insensitive lookup

class allChemicals(models.Model):
    chemID = models.IntegerField(primary_key=True)
    chemMaterial = models.CharField(max_length=255) 
    chemName = models.CharField(max_length=255)
    chemLocationRoom = models.CharField(max_length=255, default="None")
    chemLocationCabinet = models.CharField(max_length=255, default="None")
    chemLocationShelf = models.CharField(max_length=255, default="None")
    chemAmountTotal = models.FloatField(max_length=255, null=True, blank=True, default=0)
    chemAmountExpected = models.FloatField(max_length=255, null=True, blank=True, default=0) 
    chemAmountPercentage = models.FloatField(max_length=255, null=True, blank=True, default=0)
    chemAmountUnit = models.CharField(max_length=255, null=True, blank=True)
    chemConcentration = models.CharField(max_length=255, null=True, blank=True)
    chemSDS = models.CharField(max_length=20, null=True, blank=True)
    chemNotes = models.CharField(max_length=255, null=True, blank=True)
    chemInstrument = models.CharField(null = True, max_length=255)

    def __str__(self):
        return self.chemName

    def update_total_amount(self):
        total_amount = individualChemicals.objects.filter(chemAssociated=self).aggregate(Sum('chemAmountInBottle'))['chemAmountInBottle__sum'] or 0
        self.chemAmountTotal = total_amount
        if self.chemAmountExpected > 0:
            self.chemAmountPercentage = (total_amount / self.chemAmountExpected) * 100
        else:
            self.chemAmountPercentage = 0
        self.save()
    class Meta:
        db_table = "allchemicalstable"
        
class individualChemicals(models.Model):
    chemBottleIDNUM = models.IntegerField(primary_key=True) 
    chemAssociated = models.ForeignKey(allChemicals, null=True, blank=True, on_delete=models.CASCADE, default=1)
    chemMaterial = models.CharField(max_length=255, null=True, blank=True)  # New field
    chemLocationRoom = models.CharField(max_length=255, default="None")
    chemLocationCabinet = models.CharField(max_length=255, default="None")
    chemLocationShelf = models.CharField(max_length=255, default="None")
    chemAmountInBottle = models.CharField(max_length=255, default="0")
    chemCheckedOut = models.BooleanField(default=False)
    chemCheckedOutBy = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    chemCheckedOutDate = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "currentlyinstoragetable"

# Signal to populate chemMaterial before saving individualChemicals
@receiver(pre_save, sender=individualChemicals)
def populate_chem_material(sender, instance, **kwargs):
    if instance.chemAssociated:
        instance.chemMaterial = instance.chemAssociated.chemMaterial

class QRCodeData(models.Model):
    qr_code = models.CharField(max_length=255, unique=True)  # Field to store the QR code data
    name = models.CharField(max_length=255)  # Example additional field
    description = models.TextField(blank=True, null=True)  # Example additional field

    def __str__(self):
        return self.name

# Signal to update total amount when a record is saved in individualChemicals
@receiver(post_save, sender=individualChemicals)
def update_total_amount_on_save(sender, instance, **kwargs):
    if instance.chemAssociated:
        instance.chemAssociated.update_total_amount()

# Signal to update total amount when a record is deleted from individualChemicals
@receiver(post_delete, sender=individualChemicals)
def update_total_amount_on_delete(sender, instance, **kwargs):
    if instance.chemAssociated_id:  # Check if the foreign key ID exists
        try:
            associated_chemical = allChemicals.objects.get(pk=instance.chemAssociated_id)
            associated_chemical.update_total_amount()
        except allChemicals.DoesNotExist:
            # The associated allChemicals instance no longer exists, so we can safely ignore this.
            pass

class Log(models.Model):
    user = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.action
