# Generated by Django 4.2.16 on 2024-12-31 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CompareImages', '0031_rename_categories_compareimagemodels_categories1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='compareimagemodels',
            name='result',
            field=models.CharField(default='', max_length=250),
        ),
    ]