# Generated by Django 2.1.10 on 2019-07-25 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vinwash', '0002_auto_20190725_2030'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vin_conflicts',
            name='cnflict_business',
        ),
        migrations.RemoveField(
            model_name='vin_conflicts',
            name='conflict_filename',
        ),
        migrations.RemoveField(
            model_name='vin_conflicts',
            name='originalvins_business',
        ),
        migrations.AddField(
            model_name='vin_conflicts',
            name='current_occurence_fileid',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='vin_conflicts',
            name='previous_occurence_fileid',
            field=models.IntegerField(null=True),
        ),
    ]