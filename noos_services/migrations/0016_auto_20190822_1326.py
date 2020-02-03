# Generated by Django 2.2.3 on 2019-08-22 13:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('noos_services', '0015_auto_20190814_0728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simulationelement',
            name='next_element',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='noos_services.SimulationElement'),
        ),
        migrations.AlterField(
            model_name='simulationelement',
            name='previous_element',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='noos_services.SimulationElement'),
        ),
    ]
