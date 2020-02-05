# Generated by Django 2.2.5 on 2019-10-04 08:07

from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('noos_services', '0017_auto_20190930_1615'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='simulationelement',
            name='element_type',
        ),
        migrations.RemoveField(
            model_name='simulationelement',
            name='forcing_couple',
        ),
        migrations.RemoveField(
            model_name='simulationelement',
            name='node',
        ),
        migrations.RemoveField(
            model_name='simulationelement',
            name='noos_model',
        ),
        migrations.CreateModel(
            name='SimulationMetadata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('metadata', jsonfield.fields.JSONField(default=dict)),
                ('simulation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='simulation_metadata', to='noos_services.SimulationDemand')),
            ],
        ),
        migrations.CreateModel(
            name='SimulationCloud',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('idx', models.IntegerField()),
                ('cloud_data', jsonfield.fields.JSONField(default=dict)),
                ('forcing_coupple', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='simulation_clouds', to='noos_services.ForcingCouple')),
                ('node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='simulation_clouds', to='noos_services.Node')),
                ('noos_model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='simulation_clouds', to='noos_services.NoosModel')),
                ('simulation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='simulation_clouds', to='noos_services.SimulationDemand')),
            ],
        ),
    ]