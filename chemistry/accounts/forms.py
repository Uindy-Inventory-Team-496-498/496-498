from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = User  # Use the custom user model here
        fields = ['username', 'email', 'password']  # Add any additional fields if necessary

    # Optionally, add custom validation or fields if needed

class CustomLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username does not exist.")
        
        # Additional validation logic can be added here
        return cleaned_data
