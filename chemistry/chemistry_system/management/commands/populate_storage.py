import random
from django.core.management.base import BaseCommand
from chemistry_system.models import currentlyInStorageTable, allChemicalsTable, User
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populate currentlyInStorageTable with dummy data'

    def handle(self, *args, **kwargs):
        # Clear existing data
        currentlyInStorageTable.objects.all().delete()

        # Get all chemical records
        all_chemicals = list(allChemicalsTable.objects.all())

        # Generate dummy data
        bottle_id = 1
        for chem in all_chemicals:
            for _ in range(1):  # Create x bottles for each chemical

                currentlyInStorageTable.objects.create(
                    chemBottleIDNUM=bottle_id,
                    chemAssociated=chem,
                    chemLocationRoom=chem.chemLocationRoom,
                    chemLocationCabinet=random.choice(['Cabinet A', 'Cabinet B', 'Cabinet C']),
                    chemLocationShelf=random.choice(['Shelf 1', 'Shelf 2', 'Shelf 3']),
                    chemAmountInBottle=f"{random.randint(1, 1000)} mL",
                )
                bottle_id += 1

        self.stdout.write(self.style.SUCCESS('Successfully populated currentlyInStorageTable with dummy data'))