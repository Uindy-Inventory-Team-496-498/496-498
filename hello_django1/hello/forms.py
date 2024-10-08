from django import forms
from hello.models import LogChemical

class LogChemicalForm(forms.ModelForm):
    class Meta:
        model = LogChemical
        fields = ("chemical",) #Trailing comma is required