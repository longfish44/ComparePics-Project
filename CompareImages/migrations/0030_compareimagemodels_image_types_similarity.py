# Generated by Django 4.2.16 on 2024-12-31 05:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CompareImages', '0029_compareimagemodels_diffimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='compareimagemodels',
            name='image_types_similarity',
            field=models.BooleanField(default=False),
        ),
    ]