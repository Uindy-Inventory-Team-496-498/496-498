from django import forms
from hello.models import LogMessage
from django.contrib.auth.forms import AuthenticationForm


class LogMessageForm(forms.ModelForm):
    class Meta:
        model = LogMessage
        fields = ("message",) #Trailing comma is required

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label='Username', max_length=150)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)