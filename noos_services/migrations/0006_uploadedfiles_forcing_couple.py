# Generated by Django 2.1.7 on 2019-03-27 10:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('noos_services', '0005_log_messages_forcing_couple'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uploadedfile',
            name='forcing',
        ),
        migrations.AddField(
            model_name='uploadedfile',
            name='forcing_couple',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='uploadedfiles', to='noos_services.ForcingCouple'),
        ),
    ]
