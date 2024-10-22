from django.db import models
from django.utils import timezone

class LogMessage(models.Model):
    message = models.CharField(max_length=300)
    log_date = models.DateTimeField("date logged")
    def __str__(self):
        """Returns a string representation of a message"""
        date = timezone.get_current_timezone(self.log_date)
        return f"'{self.message}' logged on {date.strftime('%A, %d %B, %Y at %X')}"
	
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
