# Generated by Django 4.2.16 on 2024-12-31 01:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CompareImages', '0027_alter_documentmodels_created_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentmodels',
            name='document',
            field=models.FileField(default='', upload_to='compareimages/documents/'),
        ),
    ]
