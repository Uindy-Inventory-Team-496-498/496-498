from dal import autocomplete
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from chemistry_system.models import individualChemicals, allChemicals, get_model_by_name

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label='Username', max_length=150)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

def get_dynamic_form(model_name):
    model_info = get_model_by_name(model_name)
    if not model_info:
        raise ValueError(f"Model '{model_name}' not found.")
    
    model, required_fields = model_info

    class DynamicChemicalForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(DynamicChemicalForm, self).__init__(*args, **kwargs)
            # Set required fields
            for field_name in required_fields:
                if field_name in self.fields:
                    self.fields[field_name].required = True
            # Set other fields as not required
            for field_name, field in self.fields.items():
                if field_name not in required_fields:
                    field.required = False
                    
        class Meta:
            model_class = get_model_by_name(model_name)
            model = model_class[0]
            fields = '__all__'  # Include all fields from the model

    return DynamicChemicalForm

class AllChemicalForm(forms.ModelForm):
    class Meta:
        model = allChemicals
        fields = '__all__'  # Include all fields from the model

class IndividualChemicalsForm(forms.ModelForm):
    chemAssociated = forms.ModelChoiceField(
        queryset=allChemicals.objects.all(),
        label="Associated Chemical",
        widget=autocomplete.ModelSelect2(
            url='chemical-autocomplete',
            attrs={
                'class': 'form-control', 
                'data-placeholder': 'Start typing...',
                'data-minimum-input-length': 0
                }
            ),
        to_field_name='chemID'
    )

    class Meta:
        model = individualChemicals
        fields = '__all__'  # Include all fields from the model

class CSVUploadForm(forms.Form):
    file = forms.FileField()