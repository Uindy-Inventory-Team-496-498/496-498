from django.db import models
from django.utils import timezone
	
class currentlyInStorageTable(models.Model):
	chemBottleIDNUM = models.IntegerField()
	chemName = models.CharField(max_length=255)
	chemLocationCabinet = models.CharField(null = True, max_length=255)
	chemLocationShelf = models.CharField(null = True,max_length=255)
	chemAmountInBottle = models.FloatField()
	chemAmountUnit = models.CharField(null = True, max_length=255)
	chemConcentration = models.CharField(null = True, max_length=255)
	chemSDS = models.IntegerField(null = True)
	chemStorageType = models.CharField(max_length=255)
	
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

	material_type = models.CharField(max_length=50, choices=MATERIAL_TYPE_CHOICES)
	name = models.CharField(max_length=255)
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
