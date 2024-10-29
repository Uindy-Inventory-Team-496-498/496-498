# Generated by Django 5.1.2 on 2024-10-28 22:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='allChemicalsTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chemName', models.CharField(max_length=255)),
                ('chemLocation', models.CharField(max_length=255)),
                ('chemStorageType', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='currentlyInStorageTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chemBottleIDNUM', models.IntegerField()),
                ('chemName', models.CharField(max_length=255)),
                ('chemLocation', models.CharField(max_length=255)),
                ('chemAmountInBottle', models.FloatField()),
                ('chemStorageType', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='LogChemical',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chemical', models.CharField(max_length=300)),
                ('log_date', models.DateTimeField(verbose_name='date logged')),
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
    ]
