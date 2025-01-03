# Generated by Django 4.2.16 on 2024-12-31 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CompareImages', '0032_compareimagemodels_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='compareimagemodels',
            name='score_chi_square',
            field=models.DecimalField(decimal_places=9, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='compareimagemodels',
            name='score_corr',
            field=models.DecimalField(decimal_places=9, default=0.0, max_digits=10),
        ),
    ]