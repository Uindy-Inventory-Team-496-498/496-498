from django import forms
from django.contrib.auth.forms import AuthenticationForm
from hello.models import currentlyInStorageTable, allChemicalsTable, get_model_by_name

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

# class DynamicChemicalForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         model_name = kwargs.pop('model_name')
#         model = self.get_model_by_name(model_name)
#         self._meta.model = model
#         super(DynamicChemicalForm, self).__init__(*args, **kwargs)

#     @staticmethod
#     def get_model_by_name(model_name):
#         model_mapping = {
#             'currentlyinstoragetable': currentlyInStorageTable,
#             'allchemicalstable': allChemicalsTable,
#         }
#         return model_mapping.get(model_name.lower())
    
#     class Meta:
#         model = None
#         fields = '__all__'  # Include all fields from the model

class AllChemicalForm(forms.ModelForm):
    class Meta:
        model = allChemicalsTable
        fields = '__all__'  # Include all fields from the model

class CurrChemicalForm(forms.ModelForm):
    class Meta:
        model = currentlyInStorageTable
        fields = '__all__'  # Include all fields from the model
        # We can customize fields if needed:
        # fields = ['chemBottleIDNUM', 'chemName', 'chemLocation', 'chemAmountInBottle', 'chemStorageType']

class CSVUploadForm(forms.Form):
    file = forms.FileField()