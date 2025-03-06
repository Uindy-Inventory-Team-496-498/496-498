import django_filters

from .models import allChemicalsTable

class ChemicalFilter(django_filters.FilterSet):

    class Meta:

        model=allChemicalsTable
        fields = [
            'chemMaterial',
            'chemName',
            'chemLocationRoom',
        ]