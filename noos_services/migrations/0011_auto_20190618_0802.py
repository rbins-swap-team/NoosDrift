# Generated by Django 2.1.9 on 2019-06-18 08:02

from django.db import migrations
import jsonfield.fields
import noos_services.models


class Migration(migrations.Migration):

    dependencies = [
        ('noos_services', '0010_auto_20190521_0836'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simulationdemand',
            name='json_txt',
            field=jsonfield.fields.JSONField(default=dict, validators=[noos_services.models.validating_main_keys, noos_services.models.validating_simulation_type, noos_services.models.validating_start_time, noos_services.models.validating_end_time, noos_services.models.validating_drifter_data, noos_services.models.validating_initial_conditions, noos_services.models.validating_timestamp_coherence, noos_services.models.validating_booleans]),
        ),
    ]
