from django import forms
from hello.models import LogChemical
from django.contrib.auth.forms import AuthenticationForm

class LogChemicalForm(forms.ModelForm):
    class Meta:
        model = LogChemical
        fields = ("chemical",) #Trailing comma is required

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label='Username', max_length=150)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)