# Generated by Django 4.2.16 on 2024-12-28 08:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CompareImages', '0017_remove_compareimagemodels_url1_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='compareimagemodels',
            name='Azure_used_count',
        ),
    ]