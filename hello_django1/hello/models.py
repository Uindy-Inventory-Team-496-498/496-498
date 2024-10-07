from django.db import models
from django.utils import timezone

class LogMessage(models.Model):
    message = models.CharField(max_length=300)
    log_date = models.DateTimeField("date logged")

    def __str__(self):
        """Returns a string representation of a message"""
        date = timezone.localtime(self.log_date)
        return f"'{self.message}' logged on {date.strftime('%A, %d %B, %Y at %X')}"
    
class Director(models.Model):
    name = models.CharField(max_length=15)

    def __str__(self):
        return self.name
    
class Movie(models.Model):
    title = models.CharField(max_length=25)
    director = models.ForeignKey('Director', on_delete=models.CASCADE)
    release_date = models.DateField()

    def __str__(self):
        return self.title
