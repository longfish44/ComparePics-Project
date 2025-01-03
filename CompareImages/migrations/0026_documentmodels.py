# Generated by Django 4.2.16 on 2024-12-30 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CompareImages', '0025_alter_apimodels_created_datetime'),
    ]

    operations = [
        migrations.CreateModel(
            name='documentModels',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=200)),
                ('document', models.FileField(default='', upload_to='compareimages/documants/')),
                ('created_datetime', models.CharField(default='', max_length=200)),
            ],
        ),
    ]
