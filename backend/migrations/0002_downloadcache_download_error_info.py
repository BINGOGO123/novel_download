# Generated by Django 3.0.2 on 2020-06-22 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='downloadcache',
            name='download_error_info',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
