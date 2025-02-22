# Generated by Django 5.1.5 on 2025-02-04 19:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='allChemicalsTable',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('material_type', models.CharField(choices=[('Acid', 'Acid'), ('Flammables', 'Flammables'), ('Non-Flammable Organics', 'Non-Flammable Organics'), ('Inorganics', 'Inorganics'), ('Household Chemicals', 'Household Chemicals'), ('Indicators', 'Indicators'), ('Biochem', 'Biochem'), ('Synthetics', 'Synthetics'), ('Instrumental Chemical', 'Instrumental Chemical')], max_length=50, null=True)),
                ('name', models.CharField(max_length=255, null=True)),
                ('concentration', models.CharField(blank=True, max_length=50, null=True)),
                ('amount', models.CharField(blank=True, max_length=50, null=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('sds', models.IntegerField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('instrument', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='QRCodeData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qr_code', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='currentlyInStorageTable',
            fields=[
                ('chemBottleIDNUM', models.IntegerField(primary_key=True, serialize=False)),
                ('chemMaterial', models.CharField(max_length=255)),
                ('chemName', models.CharField(max_length=255)),
                ('chemLocationRoom', models.CharField(default='None', max_length=255)),
                ('chemLocationCabinet', models.CharField(default='None', max_length=255)),
                ('chemLocationShelf', models.CharField(default='None', max_length=255)),
                ('chemAmountInBottle', models.CharField(default='0', max_length=255)),
                ('chemCheckedOut', models.BooleanField(default=False)),
                ('chemAmountUnit', models.CharField(max_length=255, null=True)),
                ('chemConcentration', models.CharField(max_length=255, null=True)),
                ('chemSDS', models.CharField(max_length=20, null=True)),
                ('chemStorageType', models.CharField(max_length=255, null=True)),
                ('chemNotes', models.CharField(max_length=255, null=True)),
                ('chemInstrument', models.CharField(max_length=255, null=True)),
                ('chemCheckedOutDate', models.DateTimeField(blank=True, null=True)),
                ('chemCheckedOutBy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
