# Generated by Django 5.1.2 on 2024-10-22 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0003_remove_movie_director_delete_director_delete_movie'),
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
    ]
