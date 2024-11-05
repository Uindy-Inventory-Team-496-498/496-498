from django.db import models
from django.utils import timezone
	
class currentlyInStorageTable(models.Model):
	chemBottleIDNUM = models.IntegerField()
	chemName = models.CharField(max_length=255)
	chemLocation = models.CharField(max_length=255)
	chemAmountInBottle = models.FloatField()
	chemStorageType = models.CharField(max_length=255)
	 
	 
	 
class allChemicalsTable(models.Model):
	chemName = models.CharField(max_length=255)
	chemLocation = models.CharField(max_length=255)
	chemStorageType = models.CharField(max_length=255)
      
class QRCodeData(models.Model):
    qr_code = models.CharField(max_length=255, unique=True)  # Field to store the QR code data
    name = models.CharField(max_length=255)  # Example additional field
    description = models.TextField(blank=True, null=True)  # Example additional field

    def __str__(self):
        return self.name
