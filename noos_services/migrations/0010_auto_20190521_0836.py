# Generated by Django 2.2.1 on 2019-05-21 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noos_services', '0009_auto_20190521_0830'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simulationdemand',
            name='protected',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='simulationdemand',
            name='status',
            field=models.TextField(default=''),
        ),
    ]