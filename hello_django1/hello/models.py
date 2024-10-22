from django.db import models
from django.utils import timezone

class LogChemical(models.Model):
    chemical = models.CharField(max_length=300)
    log_date = models.DateTimeField("date logged")

    def __str__(self):
        """Returns a string representation of a message"""
        date = timezone.UTC(self.log_date)
        return f"'{self.chemical}' logged on {date.strftime('%A, %d %B, %Y at %X')}"
    
