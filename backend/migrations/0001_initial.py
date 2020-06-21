# Generated by Django 3.0.2 on 2020-06-20 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DownloadCache',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.TextField()),
                ('data', models.FileField(blank=True, null=True, upload_to='')),
                ('downloaded', models.BooleanField(default=False)),
                ('download_error', models.BooleanField(default=False)),
                ('date_time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='SearchCache',
            fields=[
                ('search', models.CharField(max_length=120, primary_key=True, serialize=False)),
                ('data', models.TextField()),
                ('date_time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='SearchToken',
            fields=[
                ('token', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('data', models.TextField()),
                ('date_time', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
