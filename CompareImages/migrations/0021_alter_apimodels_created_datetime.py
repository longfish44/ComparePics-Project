# Generated by Django 4.2.16 on 2024-12-30 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CompareImages', '0020_apimodels_delete_testmodels'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apimodels',
            name='created_datetime',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]