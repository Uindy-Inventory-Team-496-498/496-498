from django import forms
from hello.models import LogChemical
from django.contrib.auth.forms import AuthenticationForm
from hello.models import currentlyInStorageTable


class LogChemicalForm(forms.ModelForm):
    class Meta:
        model = LogChemical
        fields = ("chemical",) #Trailing comma is required

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label='Username', max_length=150)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
class EditChemicalForm(forms.ModelForm):
    class Meta:
        model = currentlyInStorageTable
        fields = '__all__'  # Include all fields from the model
        # We can customize fields if needed:
        # fields = ['chemBottleIDNUM', 'chemName', 'chemLocation', 'chemAmountInBottle', 'chemStorageType']