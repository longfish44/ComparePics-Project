# Generated by Django 4.2.16 on 2025-01-01 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CompareImages', '0034_alter_compareimagemodels_score_chi_square_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='compareFolderModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('newImages', models.FileField(upload_to='newImages/')),
                ('oldImages', models.FileField(upload_to='oldImages/')),
            ],
        ),
    ]
