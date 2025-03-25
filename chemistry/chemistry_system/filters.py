import django_filters

from .models import allChemicals

class ChemicalFilter(django_filters.FilterSet):

    class Meta:

        model=allChemicals
        fields = [
            'chemMaterial',
            'chemName',
            'chemLocationRoom',
        ]