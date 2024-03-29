# Generated by Django 2.2.6 on 2019-12-16 09:16

from django.db import migrations
import jsonfield.fields
import noos_services.models
import noos_services.validationhelper


class Migration(migrations.Migration):

    dependencies = [
        ('noos_services', '0019_auto_20191004_0905'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simulationdemand',
            name='json_txt',
            field=jsonfield.fields.JSONField(default=dict, validators=[noos_services.validationhelper.ValidationHelper.validating_main_keys, noos_services.models.validating_simulation_type, noos_services.models.validating_start_time, noos_services.models.validating_end_time, noos_services.models.validating_drifter_data, noos_services.models.validating_initial_conditions, noos_services.models.validating_timestamp_coherence, noos_services.models.validating_booleans]),
        ),
    ]
