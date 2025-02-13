import csv
from django.core.management.base import BaseCommand
from chemistry_system.models import currentlyInStorageTable

class Command(BaseCommand):
    help = 'Load data from CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        with open(csv_file, newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                currentlyInStorageTable.objects.update_or_create(
                    chemBottleIDNUM=row['chemBottleIDNUM'],
                    defaults={
                        'chemMaterial': row['chemMaterial'],
                        'chemName': row['chemName'],
                        'chemConcentration': row['chemConcentration'],
                        'chemAmountInBottle': row['chemAmountInBottle'],  # Ensure this is a string
                        'chemAmountUnit': row['chemAmountUnit'],
                        'chemLocationRoom': row['chemLocationRoom'],
                        'chemLocationCabinet': row['chemLocationCabinet'],
                        'chemLocationShelf': row['chemLocationShelf'],
                        'chemStorageType': row['chemStorageType'],
                        'chemSDS': row['chemSDS'],
                        'chemNotes': row['chemNotes'],
                        'chemInstrument': row['chemInstrument']
                    }
                )
        self.stdout.write(self.style.SUCCESS('Data loaded successfully'))