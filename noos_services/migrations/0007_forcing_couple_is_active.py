# Generated by Django 2.1.7 on 2019-03-27 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noos_services', '0006_uploadedfiles_forcing_couple'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='forcing',
            name='is_active',
        ),
        migrations.AddField(
            model_name='forcingcouple',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
