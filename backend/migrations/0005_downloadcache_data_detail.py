# Generated by Django 3.0.2 on 2020-07-23 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_downloadcache_data_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='downloadcache',
            name='data_detail',
            field=models.TextField(blank=True, null=True),
        ),
    ]
