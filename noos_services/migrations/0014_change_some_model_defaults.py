# Generated by Django 2.2.3 on 2019-08-12 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noos_services', '0013_add_simulation_elements'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simulationelement',
            name='element_type',
            field=models.TextField(default='C'),
        ),
    ]
