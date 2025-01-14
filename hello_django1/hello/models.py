from django.db import models
from django.utils import timezone

class LogChemical(models.Model):
    chemical = models.CharField(max_length=300)
    log_date = models.DateTimeField("date logged")
    def __str__(self):
        """Returns a string representation of a message"""
        date = timezone.UTC(self.log_date)
        return f"'{self.chemical}' logged on {date.strftime('%A, %d %B, %Y at %X')}"
	
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
	chemName = models.CharField(max_length=255)
	chemLocation = models.CharField(max_length=255)
	chemStorageType = models.CharField(max_length=255)
      
class QRCodeData(models.Model):
    qr_code = models.CharField(max_length=255, unique=True)  # Field to store the QR code data
    name = models.CharField(max_length=255)  # Example additional field
    description = models.TextField(blank=True, null=True)  # Example additional field

    def __str__(self):
        return self.name
