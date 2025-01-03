# Generated by Django 4.2.16 on 2024-12-23 02:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CompareImages', '0008_compareimagemodels_categories_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='compareimagemodels',
            name='categories_similarity',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=3),
        ),
        migrations.AddField(
            model_name='compareimagemodels',
            name='colors_similarity',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='compareimagemodels',
            name='descriptions_similarity',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='compareimagemodels',
            name='image_objects_similarity',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=3),
        ),
    ]
