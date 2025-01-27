from django.db import models
from django.utils import timezone
	
def get_model_by_name(model_name):
    model_mapping = {
        'currentlyinstoragetable': (currentlyInStorageTable, ['chemBottleIDNUM', 'chemName', 'chemLocationCabinet', 'chemAmountInBottle']),
        'allchemicalstable': (allChemicalsTable, ['id', 'name']),
    }
    return model_mapping.get(model_name.lower())

class currentlyInStorageTable(models.Model):
	chemBottleIDNUM = models.IntegerField(primary_key=True)
	chemMaterial = models.CharField(max_length=255)  # Add this line back
	chemName = models.CharField(max_length=255)
	chemLocationRoom = models.CharField(max_length=255, default="None")
	chemLocationCabinet = models.CharField(max_length=255, default="None")
	chemLocationShelf = models.CharField(max_length=255, default="None")
	chemAmountInBottle = models.CharField(max_length=255, default="0")
	chemAmountUnit = models.CharField(null = True, max_length=255)
	chemConcentration = models.CharField(null = True, max_length=255)
	chemSDS = models.CharField(null = True, max_length=1)
	chemStorageType = models.CharField(null = True, max_length=255)
	chemNotes = models.CharField(null = True, max_length=255)
	chemInstrument = models.CharField(null = True, max_length=255)
	chemTest = models.CharField(null = True, max_length=255)
	# def save(self, *args, **kwargs):
	# 	if self.chemBottleIDNUM is None:  # Check if chemBottleIDNUM is not set
	# 		max_id = currentlyInStorageTable.objects.aggregate(models.Max('chemBottleIDNUM'))['chemBottleIDNUM__max']
	# 		self.chemBottleIDNUM = (max_id or 0) + 1
	# 	super(currentlyInStorageTable, self).save(*args, **kwargs)

class allChemicalsTable(models.Model):
	MATERIAL_TYPE_CHOICES = [
        ('Acid', 'Acid'),
        ('Flammables', 'Flammables'),
        ('Non-Flammable Organics', 'Non-Flammable Organics'),
        ('Inorganics', 'Inorganics'),
        ('Household Chemicals', 'Household Chemicals'),
        ('Indicators', 'Indicators'),
        ('Biochem', 'Biochem'),
        ('Synthetics', 'Synthetics'),
        ('Instrumental Chemical', 'Instrumental Chemical'),
    ]
	id = models.IntegerField(primary_key=True)
	material_type = models.CharField(max_length=50, choices=MATERIAL_TYPE_CHOICES, null=True)
	name = models.CharField(max_length=255, null=True)
	concentration = models.CharField(max_length=50, blank=True, null=True)
	amount = models.CharField(max_length=50, blank=True, null=True)
	location = models.CharField(max_length=255, blank=True, null=True)
	sds = models.IntegerField(blank=True, null=True)
	notes = models.TextField(blank=True, null=True)
	instrument = models.CharField(max_length=255, blank=True, null=True)

	def __str__(self):
		return self.name
      
class QRCodeData(models.Model):
    qr_code = models.CharField(max_length=255, unique=True)  # Field to store the QR code data
    name = models.CharField(max_length=255)  # Example additional field
    description = models.TextField(blank=True, null=True)  # Example additional field

    def __str__(self):
        return self.name
